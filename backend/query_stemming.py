import pandas as pd
import re
from nltk.stem import PorterStemmer
from preprocess import tokenize
# Stemmer
stemmer = PorterStemmer()

def stem_list(tokens):
    return [stemmer.stem(t) for t in tokens]

# TODO: stem on query 
# input: list of tokens that represent a query
# output: stemmed list of tokens that represent a query
def stem_input(tokens):
    porter_stemmer = PorterStemmer()
    stemmed_words = [porter_stemmer.stem(word) for word in tokens]
    return stemmed_words