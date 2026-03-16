import json
import os
import requests
import time

# AI GENERATED
# because the API has a 500 page limit, downloading all reality tv shows at once will fail
# increment in buckets (first year the show was aired), save the current year to checkpoint.json
# all outputs are incremented into reality_tv.jsonl
# combine_json.py will combine the outputs of reality_tv.jsonl into 1 json file (tmdb.json)

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzN2FlNzg2Yjc5ZWEyNWVmMGMxNDEyYTkxMTI1MTNiNiIsIm5iZiI6MTc3MzEyMjUyNS43OCwic3ViIjoiNjlhZmIzZGQ2MGI3NzdlYTQ2ZmNjNjNkIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.L31hFzGQoERaVC9SikPqQCPKrdpsFH7RJWAWkwhayc8"
BASE_URL = "https://api.themoviedb.org/3/discover/tv"
GENRE_ID = 10764  # Reality

OUTFILE = "reality_tv.jsonl"
CHECKPOINT = "checkpoint.json"

START_YEAR = 1900
END_YEAR = 2026  # adjust if needed

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"year": START_YEAR, "page": 1}

def save_checkpoint(year, page):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump({"year": year, "page": page}, f)

def load_seen_ids():
    seen = set()
    if os.path.exists(OUTFILE):
        with open(OUTFILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                seen.add(obj["id"])
    return seen

def fetch_page(year, page):
    params = {
        "with_genres": GENRE_ID,
        "first_air_date_year": year,
        "sort_by": "first_air_date.asc",
        "page": page
    }
    r = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def append_results(results, seen_ids):
    added = 0
    with open(OUTFILE, "a", encoding="utf-8") as f:
        for show in results:
            show_id = show["id"]
            if show_id in seen_ids:
                continue
            f.write(json.dumps(show, ensure_ascii=False) + "\n")
            seen_ids.add(show_id)
            added += 1
    return added

def main():
    checkpoint = load_checkpoint()
    seen_ids = load_seen_ids()

    for year in range(checkpoint["year"], END_YEAR + 1):
        start_page = checkpoint["page"] if year == checkpoint["year"] else 1

        # Fetch first relevant page for this year
        first_data = fetch_page(year, start_page)
        total_pages = min(first_data.get("total_pages", 0), 500)

        if total_pages == 0:
            print(f"{year}: no results")
            save_checkpoint(year + 1, 1)
            continue

        # Process starting page
        print(f"{year}: page {start_page}/{total_pages}")
        added = append_results(first_data["results"], seen_ids)
        print(f"  added {added} new shows")
        save_checkpoint(year, start_page + 1)

        # Process remaining pages
        for page in range(start_page + 1, total_pages + 1):
            print(f"{year}: page {page}/{total_pages}")
            data = fetch_page(year, page)
            added = append_results(data["results"], seen_ids)
            print(f"  added {added} new shows")
            save_checkpoint(year, page + 1)
            time.sleep(0.1)

        # Reset to next year
        save_checkpoint(year + 1, 1)

    print("Done.")

if __name__ == "__main__":
    main()