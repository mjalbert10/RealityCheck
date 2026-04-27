import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import preprocess
from query_expansion import spell_correction
import tfidf_search
# from query_stemming import stem_list

def build_svd(k=50):

  df = preprocess.load_shows()

  # remove rows with short token lists
  df = df[df["all_tokens"].apply(len) > 2].copy()
  # join show's tokens into single string
  df["all_text"] = df["all_tokens"].apply(lambda toks: " ".join(toks))
    
  vectorizer = TfidfVectorizer(stop_words=list(preprocess.STOPWORDS), max_df = .3, 
                              min_df = 5)
  # # shows x # vocab words
  td_matrix = vectorizer.fit_transform(df["all_text"])

  # truncated SVD
  U, s, Vt = svds(td_matrix, k=k)
  order = np.argsort(-s)
  s = s[order]
  U = U[:, order]
  Vt = Vt[order, :]
  V = Vt.T

  # each vocab word has vector in latent space
  word_embeddings = Vt.T * s
  word_embeddings_normed = normalize(word_embeddings, axis=1)

  word_to_index = vectorizer.vocabulary_
  index_to_word = {i: t for t, i in word_to_index.items()}
  # each show gets vector in latent space
  doc_matrix = td_matrix @ V
  doc_matrix_normed = normalize(doc_matrix, axis=1)

  return {
    "vectorizer": vectorizer,
    "word_to_index": word_to_index,
    "index_to_word": index_to_word,
    "V": V,
    "word_embeddings": word_embeddings,
    "word_embeddings_normed": word_embeddings_normed,
    "doc_matrix_normed": doc_matrix_normed,
    "df": df,
  }

# # cosine similarity - keep k results
# def closest_words(word_in, svd, k = 10):
#   word_to_index = svd["word_to_index"]
#   index_to_word = svd["index_to_word"]
#   word_embeddings_normed = svd["word_embeddings_normed"]

#   if word_in not in word_to_index: return []

#   idx = word_to_index[word_in]
#   sims = word_embeddings_normed.dot(word_embeddings_normed[idx,:])
#   # sort highest sims to lowest
#   asort = np.argsort(-sims)[:k+1]

#   # removes query word and converts sims to floats
#   return [(index_to_word[i], float(sims[i])) for i in asort if i != idx][:k]

def embed_text(text, svd, top_n_terms=None):
    """
    Convert a full sentence/query into one vector in the SVD space.

    top_n_terms:
        optional heuristic to keep only the highest-TF-IDF query terms.
        Useful for very long noisy queries.
    """
    vectorizer = svd["vectorizer"]
    word_embeddings = svd["V"]

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

def preprocess_query_for_svd(query, svd):
    from preprocess import tokenize

    vocab = list(svd["word_to_index"].keys())

    tokens = tokenize(query)
    corrected = []

    for token in tokens:
        if token in svd["word_to_index"]:
            corrected.append(token)
        elif len(token) >= 3:
            correction = spell_correction([token], None, None, vocab)

            # Only use the correction if it is valid
            if correction is None:
                continue
            elif isinstance(correction, list) and len(correction) > 0 and correction[0]:
                corrected.append(correction[0])
            elif isinstance(correction, str) and correction:
                corrected.append(correction)

    return " ".join(corrected)

def svd_search(query, svd, df, top_k=20, genre_id=None, languages=None,
               rating=None, popularity=None, release_year=None):
    from tfidf_search import build_result
    from preprocess import tokenize

    svd_df = svd["df"].reset_index(drop=True)
    preprocessed_query = preprocess_query_for_svd(query, svd)
    q_vec = embed_text(preprocessed_query, svd)
    if q_vec is None:
        return []

    doc_matrix_normed = svd["doc_matrix_normed"]
    scores = np.array(doc_matrix_normed @ q_vec).ravel()

    top_pos = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_pos:
        if scores[i] <= 0.01:
            continue
        result = build_result(svd_df.iloc[i], scores[i])
        result["doc_idx"] = int(i)
        results.append(result)

    return results

def explain_dimension(svd, dim, top_n=8):
    index_to_word = svd["index_to_word"]
    word_embeddings = svd["word_embeddings"]

    # weights of every vocab word on this latent dimension
    weights = word_embeddings[:, dim]

    # strongest positive and strongest negative words
    pos_idx = np.argsort(-weights)[:top_n]
    neg_idx = np.argsort(weights)[:top_n]

    positive_words = [(index_to_word[i], float(weights[i])) for i in pos_idx]
    negative_words = [(index_to_word[i], float(weights[i])) for i in neg_idx]

    return {
        "dimension": int(dim),
        "positive_words": positive_words,
        "negative_words": negative_words,
    }

def hybrid_search(query, svd, df, top_k=20, genre_id=None, languages=None,
                  rating=None, popularity=None, release_year=None):

    svd_results = svd_search(
        query=query,
        svd=svd,
        df=df,
        top_k=top_k,
        genre_id=genre_id,
        languages=languages,
        rating=rating,
        popularity=popularity,
        release_year=release_year,
    )

    if svd_results:
        for r in svd_results:
            r["search_method"] = "svd"
        return svd_results

    tfidf_results = tfidf_search.tfidf_search(
        query=query,
        top_k=top_k,
        genre_id=genre_id,
        languages=languages,
        rating=rating,
        popularity=popularity,
        release_year=release_year,
    )

    for r in tfidf_results:
        r["search_method"] = "tfidf_fallback"
    return tfidf_results

def top_dimensions(query, result, svd, top_k_dims=5, top_words=6):
    q_vec, doc_vec, preprocessed_query = get_query_and_doc_vectors(query, result, svd)
    if q_vec is None:
        return None

    contrib = q_vec * doc_vec
    top_idx = np.argsort(-np.abs(contrib))[:top_k_dims]

    index_to_word = svd["index_to_word"]
    word_embeddings = svd["word_embeddings"]

    dimensions = []
    for d in top_idx:
        weights = word_embeddings[:, d]

        pos_idx = np.argsort(-weights)[:top_words]
        neg_idx = np.argsort(weights)[:top_words]

        positive_words = [index_to_word[i] for i in pos_idx]
        negative_words = [index_to_word[i] for i in neg_idx]

        if q_vec[d] >= 0 and doc_vec[d] >= 0:
            side = "positive"
            active_words = positive_words
        elif q_vec[d] < 0 and doc_vec[d] < 0:
            side = "negative"
            active_words = negative_words
        else:
            side = "mixed"
            active_words = positive_words + negative_words

        dimensions.append({
            "dimension": int(d),
            "side": side,
            "query_activation": float(q_vec[d]),
            "doc_activation": float(doc_vec[d]),
            "contribution": float(contrib[d]),
            "dimension_words": active_words
        })

    return {
        "title": result["title"],
        "score": float(result["score"]),
        "processed_query": preprocessed_query,
        "dimensions": dimensions,
    }

def get_query_and_doc_vectors(query, result, svd):
    preprocessed_query = preprocess_query_for_svd(query, svd)
    q_vec = embed_text(preprocessed_query, svd)
    if q_vec is None:
        return None, None, preprocessed_query

    doc_idx = result["doc_idx"]
    doc_vec = np.asarray(svd["doc_matrix_normed"][doc_idx]).ravel()

    return q_vec, doc_vec, preprocessed_query

explanation = {}
if __name__ == "__main__":
    svd = build_svd()
    df = preprocess.load_shows()
    query = input("Enter a word or sentence: ").strip()

    results = hybrid_search(query, svd, df)

    print("\nTop shows:")
    for result in results[:10]:
        explanation = top_dimensions(query, result, svd, top_k_dims=5, top_words=6)

        if explanation is None:
            continue
        print(result["title"])
        print("score:", result["score"])
        print("processed query:", explanation["processed_query"])

        for dim in explanation["dimensions"]:
            print(f"  dimension {dim['dimension']} ({dim['side']})")
            print(f"    query activation: {dim['query_activation']:.4f}")
            print(f"    doc activation:   {dim['doc_activation']:.4f}")
            print(f"    contribution:     {dim['contribution']:.4f}")
            print(f"    words: {', '.join(dim['dimension_words'])}")