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

def load_movies(): 
# create dataframe from json
  df = pd.read_json(DATA_PATH)

  df["name_tokens"] = df["name"].apply(tokenize)
  df["overview_tokens"] = df["overview"].apply(tokenize)

  # both name and overview tokens
  df["all_tokens"] = df["name_tokens"] + df["overview_tokens"]

  return df