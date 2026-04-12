import pandas as pd
import re
from pathlib import Path

STOPWORDS = {
    "the", "and", "is", "of", "to", "in", "a", "an", "for", "with", "on",
    "at", "by", "from", "it", "this", "that", "these", "those", "be", "as",
    "are", "was", "were", "or", "but", "if", "then", "than", "so", "do",
    "does", "did", "have", "has", "had", "about", "into", "up", "down",
    "out", "over", "under", "again", "further", "very", "can", "will", "just"
}

def tokenize(text):
    if pd.isna(text):
      return []
    text = str(text).lower()
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    return [t for t in tokens if t not in STOPWORDS]

def jaccard_sim(tokens1, tokens2):
  A, B = set(tokens1), set(tokens2)
  if not A or not B:
    return 0.0
  return len(A & B) / len(A | B)

def filter_reddit(name, overview, reddit_posts, reddit_comments, tokenize, threshold=0.02):
    meta_text = f"{name or ''} {overview or ''}"
    meta_tokens = tokenize(meta_text)

    kept_reddit_tokens = []

    for post in (reddit_posts or []):
        if isinstance(post, dict):
            item_text = f"{post.get('title', '')} {post.get('text', '')}"
        else:
            item_text = str(post)

        item_tokens = tokenize(item_text)
        if not item_tokens:
            continue

        sim = jaccard_sim(item_tokens, meta_tokens)
        if sim >= threshold:
            kept_reddit_tokens.extend(item_tokens)

    for comment in (reddit_comments or []):
        if isinstance(comment, dict):
            item_text = comment.get("text", "")
        else:
            item_text = str(comment)

        item_tokens = tokenize(item_text)
        if not item_tokens:
            continue

        sim = jaccard_sim(item_tokens, meta_tokens)
        if sim >= threshold:
            kept_reddit_tokens.extend(item_tokens)

    return kept_reddit_tokens

def build_all_tokens(row):
  name_tokens = row["name_tokens"]
  overview_tokens = row["overview_tokens"]
  reddit_tokens = row["reddit_tokens"][:100]

  all_tokens = (
      name_tokens * 5 +
      overview_tokens * 3 +
      reddit_tokens
  )
  return all_tokens

def load_shows(): 
  """Creates a dataframe from tmdb.json"""
  df = pd.read_json("src/init.json")

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)

  df["reddit_tokens"] = df.apply(
        lambda row: filter_reddit(
            row.get("name", ""),
            row.get("overview", ""),
            row.get("reddit_posts", []),
            row.get("reddit_comments", []),
            tokenize,
            threshold=0.02
        ),
        axis=1
    )

  # both name and overview tokens
  df["all_tokens"] = df.apply(build_all_tokens, axis = 1)
  return df

if __name__ == "__main__":
  load_shows()