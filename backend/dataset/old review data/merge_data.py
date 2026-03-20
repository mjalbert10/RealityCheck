import json
import re

def normalize_title(title):
    if not title:
        return None
    title = title.lower().strip()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title

with open("tmdb.json", "r", encoding="utf-8") as f:
    tmdb_data = json.load(f)

with open("reviews_tv_enriched.json", "r", encoding="utf-8") as f:
    imdb_data = json.load(f)

imdb_titles = set()
for obj in imdb_data:
    imdb = obj.get("imdb", {})
    for key in ["primaryTitle", "originalTitle"]:
        if imdb.get(key):
            imdb_titles.add(normalize_title(imdb[key]))
    for aka in imdb.get("akas", []):
        if aka.get("title"):
            imdb_titles.add(normalize_title(aka["title"]))

count = 0
examples = []

for show in tmdb_data:
    titles = set()
    if show.get("name"):
        titles.add(normalize_title(show["name"]))
    if show.get("original_name"):
        titles.add(normalize_title(show["original_name"]))

    if any(t in imdb_titles for t in titles if t):
        count += 1
        if len(examples) < 10:
            examples.append({
                "tmdb_name": show.get("name"),
                "tmdb_original_name": show.get("original_name"),
                "first_air_date": show.get("first_air_date")
            })

print("Title-only matches:", count)
print("Examples:", examples)