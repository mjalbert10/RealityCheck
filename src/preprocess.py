import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "init.json"

def tokenize(text):
    if pd.isna(text):
        return []
    text = text.lower()
    return re.findall(r"\b[a-z0-9]+\b", text)

def build_reddit_tokens(row):
    tokens = []
    posts = row.get("reddit_posts", [])
    if isinstance(posts, list):
        for post in posts:
            if isinstance(post, dict):
                tokens.extend(tokenize(post.get("title", "")))
                tokens.extend(tokenize(post.get("text", "")))
    comments = row.get("reddit_comments", [])
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                tokens.extend(tokenize(comment.get("text", "")))
    return tokens

def load_shows():
    df = pd.read_json(DATA_PATH)
    df["name_tokens"] = df["name"].apply(tokenize)
    df["overview_tokens"] = df["overview"].apply(tokenize)
    df["reddit_tokens"] = df.apply(build_reddit_tokens, axis=1)
    df["all_tokens"] = df["name_tokens"] + df["overview_tokens"] + df["reddit_tokens"]
    return df

if __name__ == "__main__":
    df = load_shows()
    print(df.loc[df["id"] == 7740, ["id", "name", "reddit_tokens"]])