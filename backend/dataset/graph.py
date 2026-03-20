import json
import matplotlib.pyplot as plt
from collections import Counter

# Load JSON
with open("tmdb.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Handle either:
# 1) {"results": [...]}  or
# 2) just a plain list [...]
if isinstance(data, dict) and "results" in data:
    shows = data["results"]
else:
    shows = data

# Extract fields
popularity = [
    show["popularity"]
    for show in shows
    if show.get("popularity") is not None
]

ratings = [
    show["vote_average"]
    for show in shows
    if show.get("vote_average") is not None
]

# For scatter plot, keep only rows that have both fields
scatter_popularity = []
scatter_ratings = []

for show in shows:
    if show.get("popularity") is not None and show.get("vote_average") is not None:
        scatter_popularity.append(show["popularity"])
        scatter_ratings.append(show["vote_average"])

# -------------------------
# 1. Popularity histogram
# -------------------------
plt.figure(figsize=(8, 5))
plt.hist(popularity, bins=30, edgecolor="black")
counts, bins, patches = plt.hist(popularity, bins=30, edgecolor="black")
plt.xlabel("Popularity")
plt.ylabel("Number of shows")
plt.title("Distribution of TMDB Popularity for Reality TV Shows")
# plt.xscale("log")   # helps because popularity is often heavily skewed
plt.ylim(0, 400)
cap = 400
for count, left, right in zip(counts, bins[:-1], bins[1:]):
    if count > cap:
        center = (left + right) / 2

        # put a label near the top of the plot
        plt.annotate(
            f"{int(count)}",
            xy=(center, cap),
            xytext=(center, cap - 80),
            ha="center",
            arrowprops=dict(arrowstyle="->")
        )
plt.tight_layout()
plt.show()

# -------------------------
# 2. Rating histogram
# -------------------------
plt.figure(figsize=(8, 5))
plt.hist(ratings, bins=20, edgecolor="black")
counts, bins, patches = plt.hist(ratings, bins=20, edgecolor="black")
plt.xlabel("Vote Average")
plt.ylabel("Number of shows")
plt.title("Distribution of TMDB Ratings for Reality TV Shows")
plt.ylim(0, 1100)
cap = 1100
for count, left, right in zip(counts, bins[:-1], bins[1:]):
    if count > cap:
        center = (left + right) / 2

        # put a label near the top of the plot
        plt.annotate(
            f"{int(count)}",
            xy=(center, cap),
            xytext=(center, cap - 80),
            ha="center",
            arrowprops=dict(arrowstyle="->")
        )
plt.tight_layout()
plt.show()

# -------------------------
# 3. Scatter plot
# -------------------------
# plt.figure(figsize=(8, 5))
# plt.scatter(scatter_popularity, scatter_ratings, alpha=0.5)
# plt.xlabel("Popularity")
# plt.ylabel("Vote Average")
# plt.title("Popularity vs Rating for Reality TV Shows")
# plt.xscale("log")
# plt.tight_layout()
# plt.show()

# -------------------------
# 4. Shows per language
# -------------------------
languages = [show["original_language"] for show in shows if show.get("original_language")]
lang_counts = Counter(languages)

# Keep top 20 languages for readability
top_langs = lang_counts.most_common(20)
labels, counts = zip(*top_langs)

plt.figure(figsize=(10, 5))
bars = plt.bar(labels, counts, edgecolor="black")
plt.xlabel("Language Code")
plt.ylabel("Number of Shows")
plt.title("Top 20 Languages — Reality TV Shows")
for bar, count in zip(bars, counts):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
             str(count), ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.show()

# -------------------------
# 5. Word count of overviews
# -------------------------
word_counts = [
    len(show["overview"].split())
    for show in shows
    if show.get("overview") and show["overview"].strip()
]

plt.figure(figsize=(8, 5))
plt.hist(word_counts, bins=30, edgecolor="black")
plt.xlabel("Word Count")
plt.ylabel("Number of Shows")
plt.title("Distribution of Overview Word Counts — Reality TV Shows")
plt.tight_layout()
plt.show()