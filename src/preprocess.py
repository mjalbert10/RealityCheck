import pandas as pd
import re
from pathlib import Path

def tokenize(text):
    if pd.isna(text):
      return []
    text = text.lower()
    return re.findall(r"\b[a-z0-9]+\b", text)
  
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

def load_shows(): 
  """Creates a dataframe from tmdb.json"""
  df = pd.read_json("dataset/tmdb.json")

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)
  df["reddit_tokens"] = df.apply(lambda row: build_reddit_tokens(row), axis=1)

  # both name and overview tokens
  df["all_tokens"] = df["name_tokens"] + df["overview_tokens"] + df["reddit_tokens"]

  # prints the whole dataframe
  # print(df[["id", "name", "name_tokens", "overview_tokens", "all_tokens", "reddit_tokens"]])
  
  # prints a single row based on ID and specific columns
  print(df.loc[df["id"] == 7740, ["id", "name", "reddit_tokens"]])
  return df

if __name__ == "__main__":
  load_shows()