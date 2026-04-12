import pandas as pd
import re
from pathlib import Path

def tokenize(text):
  if pd.isna(text):
    return []
  text = text.lower()
  return re.findall(r"\b[a-z0-9]+\b", text)
  
def load_shows(): 
  """Creates a dataframe from tmdb.json"""
  df = pd.read_json("src/init.json")
  def build_reddit_tokens(row):
    """Combines all Reddit posts and comments into a single list of tokens"""
    tokens = []

    posts = row["reddit_posts"] if "reddit_posts" in row else []
    if isinstance(posts, list):
      for post in posts:
        if isinstance(post, dict):
          tokens.extend(tokenize(post.get("title", "")))
          tokens.extend(tokenize(post.get("text", "")))

    comments = row["reddit_comments"] if "reddit_comments" in row else []
    if isinstance(comments, list):
      for comment in comments:
        if isinstance(comment, dict):
          tokens.extend(tokenize(comment.get("text", "")))

    return tokens

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)
  df["reddit_tokens"] = df.apply(lambda row: build_reddit_tokens(row), axis=1)

  # both name and overview tokens
  df["all_tokens"] = (
    df["name_tokens"].apply(lambda x: x * 5) +
    df["overview_tokens"].apply(lambda x: x * 3) +
    df["reddit_tokens"].apply(lambda x: x[:300])
)
  # prints the whole dataframe
  # print(df[["id", "name", "name_tokens", "overview_tokens", "all_tokens", "reddit_tokens"]])
  
  # prints a single row based on ID and specific columns
  # print(df.loc[df["id"] == 7740, ["id", "name", "reddit_tokens"]])
  return df

def jaccard_sim(tokens1, tokens2):
  A, B = set(tokens1), set(tokens2)
  if not A or not B:
    return 0.0
  return len(A & B) / len(A | B)

def filter_reddit(name, overview, reddit_posts, reddit_comments, tokenize, threshold = 0.02):
  meta_text = f"{name or ''} {overview or ''}"
  meta_tokens = tokenize(meta_text)

  kept_reddit_tokens = []

  reddit_items = (reddit_posts or []) + (reddit_comments or [])

  for item in reddit_items:
    item_tokens = tokenize(item)
    if not item_tokens:
      continue

    sim = jaccard_sim(item_tokens, meta_tokens)

    if sim >= threshold:
      kept_reddit_tokens.extend(item_tokens)

  return kept_reddit_tokens

def build_all_tokens(row, tokenize, reddit_threshold = 0.02):
  name_tokens = tokenize(row.get("name", ""))
  overview_tokens = tokenize(row.get("overview", ""))
  reddit_tokens = filter_reddit(
    row.get("name", ""),
    row.get("overview", ""),
    row.get("reddit_posts", []),
    row.get("reddit_comments", []), 
    tokenize,
    threshold = reddit_threshold
  )
  all_tokens = (
    name_tokens * 5 + 
    overview_tokens * 3 + 
    reddit_tokens * 1
  )
  return all_tokens

if __name__ == "__main__":
  load_shows()