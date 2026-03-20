from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

from preprocess import load_shows, tokenize

BASE_DIR = Path(__file__).parent
CACHE_PATH = BASE_DIR / "tfidf_cache.npz"
MIN_DF = 50

df = load_shows()
df = df[df["vote_average"] > 0]
df = df[df["overview"].str.strip() != ""]
df = df.dropna(subset=["overview"])
df = df.reset_index(drop=True)
N = len(df)

# ── Vocabulary ────────────────────────────────────────────────────────────────
df_counts = Counter()
for tokens in df["all_tokens"]:
    df_counts.update(set(tokens))

vocab = sorted(term for term, count in df_counts.items() if count >= MIN_DF)
term_to_idx = {term: i for i, term in enumerate(vocab)}
V = len(vocab)

idf = np.array([1 / (df_counts[term] + 1) for term in vocab])

# ── Vectorizers ───────────────────────────────────────────────────────────────
def tfidf_vectorize(tokens):
    vec = np.zeros(V)
    counts = Counter(tokens)
    for term, tf in counts.items():
        if term in term_to_idx:
            vec[term_to_idx[term]] = tf * idf[term_to_idx[term]]
    return vec

def cosine_vectorize(tokens):
    vec = np.zeros(V)
    for term in set(tokens):
        if term in term_to_idx:
            vec[term_to_idx[term]] = 1.0
    return vec

# ── Precompute or load cached matrices ────────────────────────────────────────
if CACHE_PATH.exists():
    print("Loading cached matrices...")
    cache = np.load(CACHE_PATH, mmap_mode='r')
    cosine_matrix = cache["cosine_matrix"]
else:
    print("Building matrix (first run, will cache)...")
    cosine_matrix = np.stack(df["all_tokens"].apply(cosine_vectorize).values).astype(np.float32)
    np.savez(CACHE_PATH, cosine_matrix=cosine_matrix)

cosine_norms = np.linalg.norm(cosine_matrix, axis=1)
print("Matrices ready.")

# ── Result builder ────────────────────────────────────────────────────────────
def build_result(row, score):
    return {
        "score": float(score),
        "title": row["name"],
        "description": row["overview"],
        "language": row["original_language"],
        "popularity": row["popularity"],
        "rating": row["vote_average"],
        "first_air_date": row["first_air_date"],
        "genre_ids": row["genre_ids"] if isinstance(row.get("genre_ids"), list) else [],
    }

# ── Filters ───────────────────────────────────────────────────────────────────
def apply_filters(genre_id=None, languages=None, rating=None, popularity=None, release_year=None):
    filtered = df

    if genre_id is not None:
        filtered = filtered[
            filtered["genre_ids"].apply(
                lambda ids: isinstance(ids, list) and genre_id in ids
            )
        ]

    if languages:
        filtered = filtered[filtered["original_language"].isin(languages)]

    if rating is not None:
        filtered = filtered[
            filtered["vote_average"].between(rating[0], rating[1])
        ]

    if popularity:
        if popularity == "low":
            filtered = filtered[filtered["popularity"] < 2]
        elif popularity == "medium":
            filtered = filtered[filtered["popularity"].between(2, 20)]
        elif popularity == "high":
            filtered = filtered[filtered["popularity"] > 20]

    if release_year is not None:
        def year_in_range(date):
            try:
                year = int(str(date).split("-")[0])
                return release_year[0] <= year <= release_year[1]
            except:
                return False
        filtered = filtered[filtered["first_air_date"].apply(year_in_range)]

    return filtered

# ── Search functions ──────────────────────────────────────────────────────────
def _search_with_matrix(matrix, norms, query_vec, candidates, top_k):
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return []

    idx = candidates.index.to_numpy()
    sub_matrix = matrix[idx]
    sub_norms = norms[idx]

    denom = sub_norms * query_norm
    scores = np.zeros(len(idx))
    mask = denom > 0
    scores[mask] = sub_matrix[mask] @ query_vec / denom[mask]

    top_pos = np.argsort(scores)[::-1][:top_k]
    return [build_result(candidates.iloc[i], scores[i]) for i in top_pos if scores[i] > 0.01]

def tfidf_search(query, top_k=5, genre_id=None, languages=None, rating=None,
                 popularity=None, release_year=None):
    candidates = apply_filters(genre_id, languages, rating, popularity, release_year)
    query_vec = tfidf_vectorize(tokenize(query))
    return _search_with_matrix(cosine_matrix, cosine_norms, query_vec, candidates, top_k)

def cosine_search(query, top_k=5, genre_id=None, languages=None, rating=None,
                  popularity=None, release_year=None):
    candidates = apply_filters(genre_id, languages, rating, popularity, release_year)
    query_vec = cosine_vectorize(tokenize(query))
    return _search_with_matrix(cosine_matrix, cosine_norms, query_vec, candidates, top_k)