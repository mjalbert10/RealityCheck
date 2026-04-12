import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import preprocess

def build_svd(k=200):
  df = preprocess.load_shows()

  df = df[df["all_tokens"].apply(len) > 2].copy()
  df["all_text"] = df["all_tokens"].apply(lambda toks: " ".join(toks))
    
  vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, 
                              min_df = 30)
  td_matrix = vectorizer.fit_transform(df["all_text"])

  U, s, Vt = svds(td_matrix, k=k)
  order = np.argsort(-s)
  s = s[order]
  U = U[:, order]
  Vt = Vt[order, :]

  word_embeddings = Vt.T * s
  word_embeddings_normed = normalize(word_embeddings, axis=1)

  word_to_index = vectorizer.vocabulary_
  index_to_word = {i: t for t, i in word_to_index.items()}
  return {
    "vectorizer": vectorizer,
    "word_to_index": word_to_index,
    "index_to_word": index_to_word,
    "word_embeddings": word_embeddings,
    "word_embeddings_normed": word_embeddings_normed,
  }

# cosine similarity - keep k results
def closest_words(word_in, svd, k = 10):
  word_to_index = svd["word_to_index"]
  index_to_word = svd["index_to_word"]
  word_embeddings_normed = svd["words_embeddings_normed"]

  if word_in not in word_to_index: return []

  idx = word_to_index[word_in]
  sims = word_embeddings_normed.dot(word_embeddings_normed[idx,:])
  # sort highest sims to lowest
  asort = np.argsort(-sims)[:k+1]

  # removes query word and converts sims to floats
  return [(index_to_word[i], float(sims[i])) for i in asort if i != idx][:k]

def embed_text(text, svd, top_n_terms=None):
    """
    Convert a full sentence/query into one vector in the SVD space.

    top_n_terms:
        optional heuristic to keep only the highest-TF-IDF query terms.
        Useful for very long noisy queries.
    """
    vectorizer = svd["vectorizer"]
    word_embeddings = svd["word_embeddings"]

    q_tfidf = vectorizer.transform([text])  # shape: 1 x vocab_size

    # No in-vocab words
    if q_tfidf.nnz == 0:
        return None

    # Optional: keep only the top TF-IDF terms from the query
    if top_n_terms is not None and q_tfidf.nnz > top_n_terms:
        q_tfidf = q_tfidf.tocsr(copy=True)
        keep = np.argsort(-q_tfidf.data)[:top_n_terms]

        mask = np.zeros_like(q_tfidf.data, dtype=bool)
        mask[keep] = True
        q_tfidf.data[~mask] = 0.0
        q_tfidf.eliminate_zeros()

    # Weighted combination of word vectors
    q_latent = q_tfidf @ word_embeddings   # shape: 1 x k
    q_latent = np.asarray(q_latent)

    # Normalize for cosine similarity
    norm = np.linalg.norm(q_latent)
    if norm == 0:
        return None

    return (q_latent / norm).ravel()


def closest_words_to_text(text, svd, k=10, top_n_terms=None, exclude_query_words=True):
    index_to_word = svd["index_to_word"]
    word_embeddings_normed = svd["word_embeddings_normed"]
    vectorizer = svd["vectorizer"]

    q_vec = embed_text(text, svd, top_n_terms=top_n_terms)
    if q_vec is None:
        return []

    sims = word_embeddings_normed.dot(q_vec)
    asort = np.argsort(-sims)

    query_words = set()
    if exclude_query_words:
        analyzer = vectorizer.build_analyzer()
        query_words = set(analyzer(text))

    results = []
    for i in asort:
        w = index_to_word[i]
        if exclude_query_words and w in query_words:
            continue
        results.append((w, float(sims[i])))
        if len(results) == k:
            break

    return results


if __name__ == "__main__":
    svd = build_svd()

    query = input("Enter a word or sentence: ").strip()

    print("\nClosest words:")
    for w, sim in closest_words_to_text(query, svd, k=10, top_n_terms=5):
        print(f"{w}, {sim:.3f}")