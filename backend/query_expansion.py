import pandas as pd
import re
from pathlib import Path
from nltk.corpus import wordnet
import numpy as np

# assumes query is a string but can change
def spell_correction(query, word1, word2, tokens): 
    # spell correction  (chapter 3)
    # Query expansion/reformulation with a thesaurus or WordNet (9.2)
    # query expansion via automatic thesaurus generation (9.2)
    # relevance feedback is roccio's
    # improvement: permuterm wildcard search
    # error model
    def edit_distance(word1, word2):
        i = len(word1)
        j = len(word2)
        # [[], [], [], []]
        m = np.zeros((i + 1, j + 1))
        counter = 1
        while counter <= i: 
            m[counter, 0] = counter
            counter += 1
        counter = 1
        while counter <= j: 
            m[0, counter] = counter
            counter += 1
        for l in range(1, i + 1): 
            for g in range(1, j + 1): 
                m[l][g] = min(m[l-1, g-1] + 0 if word1[l - 1] == word2[g - 1] else 1, m[l-1, g] + 1, m[l, g-1] + 1)
        return m[i, j]
    # candidate retrieval by going through inverted index tokens 
    def retrieve_corrected_words(word, tokens):
        result = []
        for token in tokens:
            score = edit_distance(word, token)
            result.append((score, token))
        result.sort(key=lambda x: x[0])
        return result
    # run for all of the words in the query (VERY SLOW?), picks top choice
    modified_query = []
    for q in query: 
        modified_query.append(retrieve_corrected_words(q, tokens)[0][1])
    return modified_query
