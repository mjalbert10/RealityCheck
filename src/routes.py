import os
from flask import send_from_directory, request, jsonify
from models import db, Episode, Review
from tfidf_search import tfidf_search


def json_search(query):
    if not query or not query.strip():
        query = "Kardashian"
    results = db.session.query(Episode, Review).join(
        Review, Episode.id == Review.id
    ).filter(
        Episode.title.ilike(f'%{query}%')
    ).all()
    matches = []
    for episode, review in results:
        matches.append({
            'title': episode.title,
            'descr': episode.descr,
            'imdb_rating': review.imdb_rating
        })
    return matches


def register_routes(app):

    @app.route("/api/episodes")
    def episodes_search():
        text = request.args.get("title", "")
        return jsonify(json_search(text))

    @app.route("/api/filters")
    def get_filters():
        from preprocess import load_movies
        from collections import Counter
        df = load_movies()

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
        query = request.args.get("q", "")
        if not query.strip():
            return jsonify([])

        year_start = request.args.get("year_start", "")
        year_end = request.args.get("year_end", "")
        languages = request.args.get("language", "")
        rating_min = request.args.get("rating_min", "")
        rating_max = request.args.get("rating_max", "")
        popularity = request.args.get("popularity", "")
        subgenre = request.args.get("subgenre", "")

        results = tfidf_search(query, top_k=50)

        lang_list = languages.split(",") if languages else []

        filtered = []
        for show in results:
            year = int(str(show["first_air_date"]).split("-")[0]) if show.get("first_air_date") else None
            if year_start and year and year < int(year_start):
                continue
            if year_end and year and year > int(year_end):
                continue

            if lang_list and show.get("language") not in lang_list:
                continue

            if rating_min and show.get("rating", 0) < float(rating_min):
                continue
            if rating_max and show.get("rating", 0) > float(rating_max):
                continue

            if popularity:
                pop = show.get("popularity", 0)
                if popularity == "low" and pop >= 2:      # replace with your 33rd percentile
                    continue
                if popularity == "medium" and not (2 <= pop < 20):  # replace with your boundaries
                    continue
                if popularity == "high" and pop < 20:     # replace with your 66th percentile
                    continue

            if subgenre and int(subgenre) not in show.get("genre_ids", []):
                continue

            filtered.append(show)

        return jsonify(filtered[:20])

    # Catch-all LAST
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')