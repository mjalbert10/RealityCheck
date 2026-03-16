import pandas as pd
import re
from pathlib import Path

p = Path("dataset/tmdb.json")
print("exists:", p.exists())
print("absolute path:", p.resolve())

df = pd.read_json("dataset/tmdb.json")

def tokenize(text):
  if pd.isna(text):
    return []
  text = text.lower()
  return re.findall(r"\b[a-z0-9]+\b", text)

df["name_tokens"] = df["name"].apply(tokenize)
df["overview_tokens"] = df["overview"].apply(tokenize)
df["all_tokens"] = df["name_tokens"] + df["overview_tokens"]

print(df[["id", "name", "name_tokens", "overview_tokens", "all_tokens"]])