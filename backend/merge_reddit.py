import json
import io
import re
import zstandard as zstd
from collections import defaultdict

tmdb_file = "dataset/tmdb.json"
submissions_file = "dataset/tvshows_submissions.zst"
comments_file = "dataset/tvshows_comments.zst"

max_posts = 50
max_comments = 100


def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Load TMDB
with open(tmdb_file, "r", encoding="utf-8") as f:
    tmdb_data = json.load(f)

show_map = {}
normalized_show_names = {}

for show in tmdb_data:
    name = show.get("name", "").strip()
    if name:
        show_map[name] = show
        show["reddit_posts"] = []
        show["reddit_comments"] = []
        normalized_show_names[name] = normalize(name)


# -----------------------------
# Speed optimization
# -----------------------------
shows_by_first_word = defaultdict(list)

for original_name, norm_name in normalized_show_names.items():
    words = norm_name.split()
    if words:
        shows_by_first_word[words[0]].append((original_name, norm_name))


def find_matching_shows(text):
    norm_text = normalize(text)
    if not norm_text:
        return []

    text_words = set(norm_text.split())
    candidate_shows = []

    for word in text_words:
        if word in shows_by_first_word:
            candidate_shows.extend(shows_by_first_word[word])

    matched = []
    for original_name, norm_name in candidate_shows:
        if norm_name in norm_text:
            matched.append(original_name)

    return list(set(matched))

# Process Reddit files
def process_zst(file_path, is_comment=False, limit=None):
    with open(file_path, "rb") as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            text_stream = io.TextIOWrapper(reader, encoding="utf-8", errors="ignore")

            for i, line in enumerate(text_stream):

                if i % 10000 == 0:
                    print(f"{file_path}: processed {i} lines")

                if limit is not None and i >= limit:
                    break

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if is_comment:
                    text = obj.get("body", "") or ""
                else:
                    title = obj.get("title", "") or ""
                    selftext = obj.get("selftext", "") or ""
                    text = f"{title} {selftext}"

                matched_shows = find_matching_shows(text)

                for show_name in matched_shows:
                    if is_comment:
                        if len(show_map[show_name]["reddit_comments"]) < max_comments:
                            show_map[show_name]["reddit_comments"].append({
                                "text": obj.get("body"),
                                "score": obj.get("score"),
                                "created_utc": obj.get("created_utc")
                            })
                    else:
                        if len(show_map[show_name]["reddit_posts"]) < max_posts:
                            show_map[show_name]["reddit_posts"].append({
                                "title": obj.get("title"),
                                "text": obj.get("selftext"),
                                "score": obj.get("score"),
                                "created_utc": obj.get("created_utc")
                            })

# Run
print("Processing submissions...")
process_zst(submissions_file, is_comment=False)

print("Processing comments...")
process_zst(comments_file, is_comment=True)

# Save back to TMDB file
with open(tmdb_file, "w", encoding="utf-8") as f:
    json.dump(tmdb_data, f, indent=2)

print("tmdb.json updated with Reddit data")