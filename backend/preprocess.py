import pandas as pd
import re
from pathlib import Path

def load_shows(): 
  """Creates a dataframe from tmdb.json"""
  df = pd.read_json("dataset/tmdb.json")

  def tokenize(text):
    if pd.isna(text):
      return []
    text = text.lower()
    return re.findall(r"\b[a-z0-9]+\b", text)

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)

  # both name and overview tokens
  df["all_tokens"] = df["name_tokens"] + df["overview_tokens"]

  print(df[["id", "name", "name_tokens", "overview_tokens", "all_tokens"]])
  return df