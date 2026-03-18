from collections import Counter
import numpy as np

from preprocess import load_movies, tokenize

df = load_movies()

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

# Convert docs to vectors/Cosine Simliarity 
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