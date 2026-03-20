from collections import Counter
import numpy as np

from preprocess import load_shows, tokenize

df = load_shows()

TOTAL_SHOWS = 17017

# Make vocabulary
vocab = set()
for tokens in df["all_tokens"]:
    vocab.update(tokens)

vocab = sorted(vocab)
term_to_idx = {term: i for i, term in enumerate(vocab)}

V = len(vocab)
N = len(df)

# DF
df_counts = Counter()
for tokens in df["all_tokens"]:
    df_counts.update(set(tokens))

# IDF
idf = np.zeros(V)
for term, idx in term_to_idx.items():
    df_count = df_counts.get(term, 0)
    idf[idx] = 1 / (df_count + 1)
    # idf[idx] = np.log((TOTAL_SHOWS + 1) / (df_count + 1)) + 1

# Convert docs to vectors
def vectorize(tokens):
    vec = np.zeros(V)
    counts = Counter(tokens)

    for term, tf in counts.items():
        if term in term_to_idx:
            idx = term_to_idx[term]
            vec[idx] = tf * idf[idx]
    return vec

# TF-IDF
df["tfidf_vec"] = df["all_tokens"].apply(vectorize)

# Cosine similarity
def cosine_sim(v1, v2):
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                             
def tfidf_search(query, top_k = 5):
    query_tokens = tokenize(query)
    query_vec = vectorize(query_tokens)

    scores = []

    for _, row in df.iterrows():
        score = cosine_sim(query_vec, row["tfidf_vec"])
        if score > 0:
            scores.append((score, row["name"]))
    
    scores.sort(reverse = True)
    return scores[:top_k]


def apply_filters(df, genre_id=None, language=None, rating=None, traffic=None,
                  release_year=None):
    """
    Narrows down the TMDB dataframe to only have filtered results

    Note: rating and release_year must have 2 elements in their lists
    """
    # all inputs should be lists (even if only 1 element)
    filtered = df

    if genre_id is not None:
        # boolean masks for each result
        filtered = filtered[
            filtered["genre_ids"].apply(
                lambda genres: isinstance(genres, list) and genre_id in genres
            )
        ]
    if language is not None:
        # filtered = filtered[filtered["original_language"] == language]
        filtered = filtered[
            filtered["original_language"].apply(
                lambda langs: isinstance(langs, list) and language in langs
            )
        ]
    if rating is not None:
        # filtered = filtered[filtered["vote_average"] == rating]
        filtered = filtered[
            filtered["vote_average"].apply(
                lambda vote_avg: True if rating[0] <= vote_avg <= rating[1] else False
            )
        ]
    # ADJUST LOGIC
    # if traffic is not None:
    #     filtered = filtered[
    #         filtered["popularity"].apply(
    #             lambda popularity: isinstance(popularity, list) and traffic in popularity
    #         )
    #     ]
    if release_year is not None:
        # filtered = filtered[filtered["first_air_date"] == release_year]
        filtered = filtered[
            filtered["first_air_date"].apply(
                lambda date: True if release_year[0] <= date <= release_year[1] else False
            )
        ]
    return filtered


def search(query, top_k=5, genre_id=None, language=None, rating=None, traffic=None,
                  release_year=None):
    """Uses filters along with tfdidf_search"""
    candidates = apply_filters(
        df,
        genre_id=genre_id,
        language=language,
        rating=rating,
        traffic=traffic,
        release_year=release_year
    )
    return tfidf_search(query, candidates, top_k=top_k)