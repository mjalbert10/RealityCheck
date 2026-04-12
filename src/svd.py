import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import preprocess

def build_svd():
  df = preprocess.load_shows()

  df = df[df["all_tokens"].apply(len) > 2].copy()
  df["all_text"] = df["all_tokens"].apply(lambda toks: " ".join(toks))
    
  vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, 
                              min_df = 75)
  td_matrix = vectorizer.fit_transform(df["all_text"])

  docs_compressed, s, words_compressed = svds(td_matrix, k=40)
  words_compressed = words_compressed.transpose() * s

  word_to_index = vectorizer.vocabulary_
  index_to_word = {i:t for t,i in word_to_index.items()}

  words_compressed_normed = normalize(words_compressed, axis = 1)
  return {
    "word_to_index": word_to_index,
    "index_to_word": index_to_word,
    "words_compressed_normed": words_compressed_normed,
  }

# cosine similarity - keep k results
def closest_words(word_in, svd, k = 10):
  word_to_index = svd["word_to_index"]
  index_to_word = svd["index_to_word"]
  words_representation_in = svd["words_compressed_normed"]

  if word_in not in word_to_index: return []

  idx = word_to_index[word_in]
  sims = words_representation_in.dot(words_representation_in[idx,:])
  # sort highest sims to lowest
  asort = np.argsort(-sims)[:k+1]

  # removes query word and converts sims to floats
  return [(index_to_word[i], float(sims[i])) for i in asort if i != idx][:k]

if __name__ == "__main__":
  word = input("enter a word: ")
  print("Using SVD matrix:")
  for w, sim in closest_words(word, build_svd()):
    try:
      print("{}, {:.3f}".format(w, sim))
    except:
      print("word not found")