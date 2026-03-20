import pandas as pd
import re
from nltk.stem import PorterStemmer

from preprocess import tokenize

# Stemmer
stemmer = PorterStemmer()

def stem_list(tokens):
    return [stemmer.stem(t) for t in tokens]

def load_reviews(file_path):
    # Load data
    df = pd.read_json(file_path)

    # CHANGE TO ACTUAL REVIEW COLUMN LATER
    text_col = "review_text"

    # Tokenize using preprocess.py
    df["review_tokens"] = df[text_col].apply(tokenize)

    # Stem
    df["review_stems"] = df["review_tokens"].apply(stem_list)

    print(df[[text_col, "review_tokens", "review_stems"]].head())

    return df

# If need to combine multiple fields
def load_reviews_multi(file_path, text_columns):
    df = pd.read_json(file_path)
    all_tokens = []
    all_stems = []

    for col in text_columns:
        if col not in df.columns:
            continue

        tokens = df[col].apply(tokenize)
        stems = tokens.appy(stem_list)

        all_tokens.append(tokens)
        all_stems.append(stems)
    if all_tokens:
        df["all_review_tokens"] = sum(all_tokens)
        df["all_review_tokens"] = sum(all_stems)
    return df

if __name__ == "__main__":
    df_reviews = load_reviews("dataset/reviews.json")
    # if multiple fields
    # df_reviews = load_reviews_multi("dataset/reivews.json", text_columns=["content", "title"])