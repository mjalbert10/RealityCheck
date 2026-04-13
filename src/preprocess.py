import pandas as pd
import re
from pathlib import Path
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

BASE_STOPWORDS = set(ENGLISH_STOP_WORDS)

DOMAIN_STOPWORDS = {
    "the", "and", "is", "of", "to", "in", "a", "an", "for", "with", "on",
    "at", "by", "from", "it", "this", "that", "these", "those", "be", "as",
    "are", "was", "were", "or", "but", "if", "then", "than", "so", "do",
    "does", "did", "have", "has", "had", "about", "into", "up", "down",
    "out", "over", "under", "again", "further", "very", "can", "will", "just"
}

STOPWORDS = BASE_STOPWORDS | DOMAIN_STOPWORDS

def tokenize(text):
    if pd.isna(text):
      return []
    text = str(text).lower()
    # Expand common contractions before stripping punctuation
    text = re.sub(r"n['’]t\b", " not", text)
    text = re.sub(r"['’]re\b", " are", text)
    text = re.sub(r"['’]ve\b", " have", text)
    text = re.sub(r"['’]ll\b", " will", text)
    text = re.sub(r"['’]m\b", " am", text)
    text = re.sub(r"['’]d\b", " would", text)
    text = re.sub(r"['’]s\b", "", text)

    # Keep letters/numbers, replace other punctuation with spaces
    text = re.sub(r"[^a-z0-9\s-]", " ", text)

    # Keep tokens that start with a letter
    tokens = re.findall(r"[a-z][a-z0-9-]*", text)

    cleaned = []
    for t in tokens:
        if len(t) < 3:
            continue
        if t.isdigit():
            continue
        if t in STOPWORDS:
            continue
        cleaned.append(t)

    return cleaned

def jaccard_sim(tokens1, tokens2):
  A, B = set(tokens1), set(tokens2)
  if not A or not B:
    return 0.0
  return len(A & B) / len(A | B)

def filter_reddit(name, overview, reddit_posts, reddit_comments, tokenize, 
                  min_overlap=2, min_ratio=0.15, max_tokens=40):
    meta_text = f"{name or ''} {overview or ''}"
    meta_tokens = tokenize(meta_text)

    kept = []

    def maybe_keep(item_text):
        item_tokens = tokenize(item_text)
        if len(item_tokens) < 4:
            return

        item_set = set(item_tokens)
        overlap = item_set & meta_tokens

        if len(overlap) >= min_overlap and len(overlap) / len(item_set) >= min_ratio:
            kept.extend(item_tokens[:20])

    for post in (reddit_posts or []):
        if isinstance(post, dict):
            item_text = f"{post.get('title', '')} {post.get('text', '')}"
        else:
            item_text = str(post)
        maybe_keep(item_text)

    for comment in (reddit_comments or []):
        if isinstance(comment, dict):
            item_text = comment.get("text", "")
        else:
            item_text = str(comment)
        maybe_keep(item_text)

    return kept[:max_tokens]

def build_all_tokens(row):
  name_tokens = row["name_tokens"]
  overview_tokens = row["overview_tokens"]

  all_tokens = (
      name_tokens * 5 +
      overview_tokens * 3
  )
  return all_tokens

def load_shows(): 
  """Creates a dataframe from tmdb.json"""
  df = pd.read_json("src/init.json")

  df = df.dropna(subset=["name", "overview"]).copy()
  df = df[df["overview"].astype(str).str.strip() != ""].reset_index(drop=True)

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)

  # Start with NO reddit
  df["all_tokens"] = df.apply(
      lambda row: row["name_tokens"] * 4 + row["overview_tokens"] * 2,
      axis=1
  )

  # Optional: string version for sklearn TfidfVectorizer
  df["doc_text"] = df["all_tokens"].apply(lambda toks: " ".join(toks))

  return df

if __name__ == "__main__":
  load_shows()