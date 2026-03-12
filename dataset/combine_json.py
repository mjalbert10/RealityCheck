import json

input_file = "reality_tv.jsonl"
output_file = "tmdb.json"

all_shows = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            all_shows.append(json.loads(line))

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_shows, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_shows)} shows to {output_file}")