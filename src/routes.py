import os
from flask import app, send_from_directory, request, jsonify
from svd import build_svd, svd_search
from tfidf_search import tfidf_search

_svd = build_svd()

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
                return jsonify([])

            model = request.args.get("model", "tfidf")
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

            try:
                results = svd_search(query, _svd, [], **kwargs)
            except Exception as e:
                print("SVD ERROR:", e)
                results = []

            # make sure it's always a list
            if not results:
                results = []

            # remove bad entries
            clean_results = []
            for r in results:
                if isinstance(r, dict):
                    clean_results.append(r)

            results = clean_results
            
            # if results are empty
            if (len(results) == 0): 
                tfidf_search(query)

            # safe sort
            results.sort(key=lambda x: x.get("score", 0), reverse=True)

            return jsonify(results)

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