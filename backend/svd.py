import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import preprocess
from query_expansion import query_expansion, spell_correction
from query_stemming import stem_list

def build_svd(k=50):
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
  doc_matrix = td_matrix @ word_embeddings
  doc_matrix_normed = normalize(doc_matrix, axis=1)

  return {
    "vectorizer": vectorizer,
    "word_to_index": word_to_index,
    "index_to_word": index_to_word,
    "word_embeddings": word_embeddings,
    "word_embeddings_normed": word_embeddings_normed,
    "doc_matrix_normed": doc_matrix_normed,
    "df": df,
  }

# cosine similarity - keep k results
def closest_words(word_in, svd, k = 10):
  word_to_index = svd["word_to_index"]
  index_to_word = svd["index_to_word"]
  word_embeddings_normed = svd["word_embeddings_normed"]

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

    tokens = preprocess.tokenize(text)
    tokens = stem_list(tokens)

    expansion = query_expansion(tokens)
    expanded_tokens = list(tokens)
    for token, (count, synonyms) in expansion.items():
        expanded_tokens.extend(synonyms[:2])

    preprocessed_query = " ".join(expanded_tokens)
    q_vec = embed_text(preprocessed_query, svd)

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

def svd_search(query, svd, df, top_k=20, genre_id=None, languages=None,
               rating=None, popularity=None, release_year=None):
    from tfidf_search import build_result
    from preprocess import tokenize

    svd_df = svd["df"].reset_index(drop=True)
    vocab = list(svd["word_to_index"].keys())

    tokens = tokenize(query)
    corrected = []
    for token in tokens:
        if token in svd["word_to_index"]:
            corrected.append(token)
        elif len(token) >= 5:
            corrected.append(spell_correction([token], None, None, vocab)[0])

    preprocessed_query = " ".join(corrected)
    q_vec = embed_text(preprocessed_query, svd)
    if q_vec is None:
        return []

    doc_matrix_normed = svd["doc_matrix_normed"]
    scores = np.array(doc_matrix_normed @ q_vec).ravel()

    top_pos = np.argsort(scores)[::-1][:top_k]
    return [build_result(svd_df.iloc[i], scores[i])
            for i in top_pos if scores[i] > 0.01]

if __name__ == "__main__":
    svd = build_svd()
    df = preprocess.load_shows()
    query = input("Enter a word or sentence: ").strip()

    print("\nTop shows:")
    for result in svd_search(query, svd, df):
        print(f"{result['title']}, {result['score']:.3f}")