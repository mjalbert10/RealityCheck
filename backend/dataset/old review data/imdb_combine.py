import json
import pandas as pd

reviews_file = "reviews.json"
basics_file = "title.basics.tsv/title.basics.tsv"
output_file = "reviews_tv_enriched.json"

allowed_types = {"tvSeries", "tvMiniSeries"}

with open(reviews_file, "r", encoding="utf-8") as f:
    reviews = json.load(f)

show_ids = {obj["Show ID"] for obj in reviews if "Show ID" in obj}

tv_info = {}

for chunk in pd.read_csv(
    basics_file,
    sep="\t",
    usecols=["tconst", "titleType", "primaryTitle", "originalTitle", "startYear", "endYear", "genres"],
    chunksize=100000,
    dtype=str,
    na_values=["\\N"]
):
    matches = chunk[
        chunk["tconst"].isin(show_ids) &
        chunk["titleType"].isin(allowed_types)
    ]

    for _, row in matches.iterrows():
        tv_info[row["tconst"]] = {
            "tconst": row["tconst"],
            "titleType": row["titleType"],
            "primaryTitle": row["primaryTitle"],
            "originalTitle": row["originalTitle"],
            "startYear": row["startYear"],
            "endYear": row["endYear"],
            "genres": row["genres"],
        }

enriched = []
for obj in reviews:
    show_id = obj.get("Show ID")
    if show_id in tv_info:
        new_obj = dict(obj)
        new_obj["imdb"] = tv_info[show_id]
        enriched.append(new_obj)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

print(f"Saved {len(enriched)} TV-review rows to {output_file}")