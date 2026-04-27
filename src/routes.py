import os
from flask import send_from_directory, request, jsonify
from svd import build_svd, svd_search, explain_why_result_matched, get_user_facing_keywords
from tfidf_search import tfidf_search
from rag import generate_answer, rewrite_query, retrieve_hits, SVD_INDEX
from infosci_spark_client import LLMClient


_client = LLMClient(api_key=os.getenv("SPARK_API_KEY"))

def register_routes(app):

    @app.route("/api/filters")
    def get_filters():
        from preprocess import load_shows
        from collections import Counter
        df = load_shows()

        lang_counts = Counter(df["original_language"].dropna().tolist())
        languages = [lang for lang, _ in lang_counts.most_common(10)]

        years = df["first_air_date"].dropna().apply(
            lambda x: str(x).split("-")[0]
        ).unique().tolist()
        years = sorted([y for y in years if str(y).isdigit()])

        all_genre_ids = set()
        for ids in df["genre_ids"].dropna():
            if isinstance(ids, list):
                all_genre_ids.update(ids)
        all_genre_ids.discard(10764)

        return jsonify({
            "languages": languages,
            "years": {"min": years[0], "max": years[-1]},
            "ratings": {
                "min": float(df["vote_average"].min()),
                "max": float(df["vote_average"].max())
            },
            "popularity": {
                "min": float(df["popularity"].min()),
                "max": float(df["popularity"].max())
            },
            "genre_ids": sorted(all_genre_ids)
        })

    @app.route("/api/search")
    def semantic_search():
        try:
            query = request.args.get("q", "")
            if not query.strip():
                return jsonify({"results": [], "answer": ""})

            model = request.args.get("type", "tfidf")
            year_start = request.args.get("year_start", "")
            year_end = request.args.get("year_end", "")
            languages = request.args.get("language", "")
            rating_min = request.args.get("rating_min", "")
            rating_max = request.args.get("rating_max", "")
            popularity = request.args.get("popularity", "")
            subgenre = request.args.get("subgenre", "")

            kwargs = {
                "top_k": 20,
                "genre_id": int(subgenre) if subgenre else None,
                "languages": languages.split(",") if languages else None,
                "rating": [float(rating_min), float(rating_max)] if rating_min and rating_max else None,
                "popularity": popularity if popularity else None,
                "release_year": [int(year_start), int(year_end)] if year_start and year_end else None,
            }

            finQuery = rewrite_query(query, _client)

            if model == "svd":
                import svd
                svd.main()
                results = svd.results
                all_result_explanations = svd.final_explanations
                '''
                results = svd_search(finQuery, SVD_INDEX, [], **kwargs)
                '''
                enriched = []
                for r in results:
                    try:
                        #explanation = explain_why_result_matched(finQuery, r, SVD_INDEX)
                        #keywords = get_user_facing_keywords(explanation)
                        # for each result, access explanation
                        dim = all_result_explanations[r]["dimensions"]
                        r["match_explanation"] = f"Matched on: {', '.join(dim['dimension_words'])}"
                        r["match_dimensions"] = dim
                    except Exception:
                        r["match_explanation"] = None
                        r["match_dimensions"] = {}
                    enriched.append(r)
                results = enriched
            else:
                # Default: TF-IDF
                results = tfidf_search(finQuery, **kwargs)
 
            rag_hits = retrieve_hits(finQuery, top_k=20)
            answer = generate_answer(query, finQuery, rag_hits, _client)
        
            # make sure it's always a list
            if not results:
                results = []
            # remove bad entries
            clean_results = []
            for r in results:
                if isinstance(r, dict):
                    clean_results.append(r)
            results = clean_results

            # safe sort
            results.sort(key=lambda x: x.get("score", 0), reverse=True)

            return jsonify({"results": results, "answer": answer})

        except Exception as e:
            print("🔥 SEARCH ERROR:", e)
            return jsonify({"error": str(e)}), 500
    
    # Catch-all LAST
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path.startswith("api"):
            return jsonify({"error": "Not found"}), 404

        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')