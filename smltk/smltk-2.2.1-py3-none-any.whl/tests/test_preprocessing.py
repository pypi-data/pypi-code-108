import unittest
from smltk.preprocessing import Ntk
import nltk
from nltk.stem import WordNetLemmatizer
from collections import Counter
import scipy
import numpy as np
import pandas as pd

class TestNtk(unittest.TestCase, Ntk):
    ntk = None
    doc = 'Good case, Excellent value. I am agree. There is a mistake. Item Does Not Match Picture.'
    docs = []
    target = []
    tuples = []
    default_doc_filtered = 'good case excellent value agree mistake item match picture'
    without_stop_words_doc_filtered = 'good case excellent value i be agree there be a mistake item do not match picture'
    without_stop_words_with_min_length_doc_filtered = 'good case excellent value be agree there be mistake item do not match picture'
    without_stop_words_without_tag_map_doc_filtered = 'good case excellent value i am agree there is a mistake item doe not match picture'
    def __init__(self, *args, **kwargs):
        self.ntk = Ntk()
        self.ntk_no_stop_words = Ntk({'stop_words': []})
        self.docs = nltk.sent_tokenize(self.doc)
        self.target = [1, 1, 0, 0]
        self.tuples = self.ntk.create_tuples(self.docs, self.target)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_get_tokens_cleaned(self):
        tokens = self.ntk_no_stop_words.get_tokens_cleaned(self.docs[0])
        self.assertEqual(tokens, ['good', 'case', 'excellent', 'value'])
        tokens = self.ntk_no_stop_words.get_tokens_cleaned(self.docs[1], is_lemma = True)
        self.assertEqual(tokens, ['i', 'be', 'agree'])
        tokens = self.ntk_no_stop_words.get_tokens_cleaned(self.docs[1], is_lemma = False)
        self.assertEqual(tokens, ['i', 'am', 'agree'])

        tokens = self.ntk.get_tokens_cleaned(self.docs[1], is_lemma = False)
        self.assertEqual(tokens, ['agree'])

    def test_get_doc_cleaned(self):
        self.assertEqual(self.ntk.get_doc_cleaned(self.doc), self.default_doc_filtered)
        self.assertEqual(self.ntk_no_stop_words.get_doc_cleaned(self.doc), self.without_stop_words_doc_filtered)

    def test_doc_cleaned(self):
        vocab_token = self.ntk.create_vocab_from_docs(self.docs, False)
        self.assertEqual(len(vocab_token), 9)
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token), (9, 9))
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token, 2), (0, 9))

        vocab_lemma = self.ntk.create_vocab_from_docs(self.docs, True)
        self.assertEqual(len(vocab_lemma), 9)
        self.assertEqual(self.ntk.get_stats_vocab(vocab_lemma), (9, 9))
        self.assertEqual(self.ntk.get_stats_vocab(vocab_lemma, 2), (0, 9))

        features_token = self.ntk.create_features_from_tuples(self.tuples, False)
        self.assertEqual(features_token[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_token = self.ntk.create_features_from_docs(self.docs[:2], 1, False)
        features_token.extend(self.ntk.create_features_from_docs(self.docs[2:], 0, False))
        self.assertEqual(features_token[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = self.ntk.create_features_from_docs(self.docs[:2], 1, True)
        features_lemma.extend(self.ntk.create_features_from_docs(self.docs[2:], 0, True))
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        words_top = self.ntk.get_words_top(vocab_token, 4)
        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True, words_top)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = self.ntk.create_features_from_docs(self.docs[:2], 1, True, words_top)
        features_lemma.extend(self.ntk.create_features_from_docs(self.docs[2:], 0, True, words_top))
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(self.ntk.get_doc_cleaned(doc, False))
        tuples = self.ntk.create_tuples(docs_cleaned, self.target)
        vocab_token = self.ntk.create_vocab_from_tuples(tuples, False)
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token), (9, 9))
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token, 2), (0, 9))

        vocab_token = self.ntk.create_vocab_from_docs(docs_cleaned, False)
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token), (9, 9))
        self.assertEqual(self.ntk.get_stats_vocab(vocab_token, 2), (0, 9))

    def test_doc_cleaned_with_lemmatizer(self):
        ntk = Ntk({'lemmatizer': WordNetLemmatizer()})
        self.assertEqual(ntk.get_doc_cleaned(self.doc), self.default_doc_filtered)

    def test_doc_cleaned_without_stop_words(self):
        vocab_token = self.ntk_no_stop_words.create_vocab_from_docs(self.docs, False)
        self.assertEqual(len(vocab_token), 16)
        self.assertEqual(vocab_token['am'], 1)
        self.assertEqual(vocab_token['is'], 1)
        self.assertEqual(vocab_token['does'], 1)
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token), (16, 16))
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token, 2), (0, 16))

        vocab_lemma = self.ntk_no_stop_words.create_vocab_from_docs(self.docs, True)
        self.assertEqual(len(vocab_lemma), 15)
        self.assertEqual(vocab_lemma['be'], 2)
        self.assertEqual(vocab_lemma['do'], 1)
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_lemma), (15, 15))
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_lemma, 2), (1, 15))

        features_token = self.ntk_no_stop_words.create_features_from_tuples(self.tuples, False)
        self.assertEqual(features_token[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = self.ntk_no_stop_words.create_features_from_tuples(self.tuples, True)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        words_top = self.ntk.get_words_top(vocab_token, 4)
        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True, words_top)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(self.ntk_no_stop_words.get_doc_cleaned(doc, False))
        tuples = self.ntk_no_stop_words.create_tuples(docs_cleaned, self.target)
        vocab_token = self.ntk_no_stop_words.create_vocab_from_tuples(tuples, False)
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token), (16, 16))
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token, 2), (0, 16))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(self.ntk_no_stop_words.get_doc_cleaned(doc, True))
        tuples = self.ntk_no_stop_words.create_tuples(docs_cleaned, self.target)
        vocab_token = self.ntk_no_stop_words.create_vocab_from_tuples(tuples)
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token), (15, 15))
        self.assertEqual(self.ntk_no_stop_words.get_stats_vocab(vocab_token, 2), (1, 15))

    def test_doc_cleaned_without_stop_words_with_min_length(self):
        ntk = Ntk({'stop_words': [], 'min_length': 2})
        self.assertEqual(ntk.get_doc_cleaned(self.doc), self.without_stop_words_with_min_length_doc_filtered)

        vocab_token = ntk.create_vocab_from_docs(self.docs, False)
        self.assertEqual(len(vocab_token), 14)
        self.assertEqual(vocab_token['am'], 1)
        self.assertEqual(vocab_token['is'], 1)
        self.assertEqual(vocab_token['does'], 1)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (14, 14))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (0, 14))

        vocab_lemma = ntk.create_vocab_from_docs(self.docs, True)
        self.assertEqual(len(vocab_lemma), 13)
        self.assertEqual(vocab_lemma['be'], 2)
        self.assertEqual(vocab_lemma['do'], 1)
        self.assertEqual(ntk.get_stats_vocab(vocab_lemma), (13, 13))
        self.assertEqual(ntk.get_stats_vocab(vocab_lemma, 2), (1, 13))

        features_token = ntk.create_features_from_tuples(self.tuples, False)
        self.assertEqual(features_token[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = ntk.create_features_from_tuples(self.tuples, True)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        words_top = self.ntk.get_words_top(vocab_token, 4)
        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True, words_top)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(ntk.get_doc_cleaned(doc, False))
        tuples = ntk.create_tuples(docs_cleaned, self.target)
        vocab_token = ntk.create_vocab_from_tuples(tuples, False)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (14, 14))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (0, 14))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(ntk.get_doc_cleaned(doc, True))
        tuples = ntk.create_tuples(docs_cleaned, self.target)
        vocab_token = ntk.create_vocab_from_tuples(tuples)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (13, 13))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (1, 13))

    def test_doc_cleaned_without_stop_words_without_tag_map(self):
        ntk = Ntk({'stop_words': [], 'tag_map': {}})
        self.assertEqual(ntk.get_doc_cleaned(self.doc), self.without_stop_words_without_tag_map_doc_filtered)

        vocab_token = ntk.create_vocab_from_docs(self.docs, False)
        self.assertEqual(len(vocab_token), 16)
        self.assertEqual(vocab_token['does'], 1)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (16, 16))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (0, 16))

        vocab_lemma = ntk.create_vocab_from_docs(self.docs, True)
        self.assertEqual(len(vocab_lemma), 16)
        self.assertEqual(vocab_lemma['doe'], 1)
        self.assertEqual(ntk.get_stats_vocab(vocab_lemma), (16, 16))
        self.assertEqual(ntk.get_stats_vocab(vocab_lemma, 2), (0, 16))

        features_token = ntk.create_features_from_tuples(self.tuples, False)
        self.assertEqual(features_token[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        features_lemma = ntk.create_features_from_tuples(self.tuples, True)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        words_top = self.ntk.get_words_top(vocab_token, 4)
        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True, words_top)
        self.assertEqual(features_lemma[1], ({'words_top': 0, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612}, 1))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(ntk.get_doc_cleaned(doc, False))
        tuples = ntk.create_tuples(docs_cleaned, self.target)
        vocab_token = ntk.create_vocab_from_tuples(tuples, False)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (16, 16))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (0, 16))

        docs_cleaned = []
        for doc in self.docs:
            docs_cleaned.append(ntk.get_doc_cleaned(doc, True))
        tuples = ntk.create_tuples(docs_cleaned, self.target)
        vocab_token = ntk.create_vocab_from_tuples(tuples)
        self.assertEqual(ntk.get_stats_vocab(vocab_token), (16, 16))
        self.assertEqual(ntk.get_stats_vocab(vocab_token, 2), (0, 16))

    def test_get_words_top(self):
        vocabs = Counter({'one': 10, 'two': 8, 'three': 4, 'four': 2, 'five': 0, 'six': 1})
        vocabs_cleaned = self.ntk.get_words_top(vocabs, 4)
        self.assertEqual(vocabs_cleaned, {'one', 'two', 'three', 'four'})

    def test_get_vocabs_cleaned(self):
        vocabs = {'one': Counter({'uno':1, 'uno':2, 'hm':3}), 'two': Counter({'due':2, 'dos':3, 'hm':4})}
        vocabs_cleaned = self.ntk.get_vocabs_cleaned(vocabs)
        self.assertEqual(vocabs_cleaned, {'one': Counter({'uno':1, 'uno':2}), 'two': Counter({'due':2, 'dos':3})})
        self.assertEqual(vocabs_cleaned, {'one': {'uno':1, 'uno':2}, 'two': {'due':2, 'dos':3}})
        vocabs = {'one': {'uno':1, 'uno':2, 'hm':3}, 'two': {'due':2, 'dos':3, 'hm':4}}
        vocabs_cleaned = self.ntk.get_vocabs_cleaned(vocabs)
        self.assertEqual(vocabs_cleaned, {'one': Counter({'uno':1, 'uno':2}), 'two': Counter({'due':2, 'dos':3})})
        self.assertEqual(vocabs_cleaned, {'one': {'uno':1, 'uno':2}, 'two': {'due':2, 'dos':3}})

    def test_get_ngrams(self):
        tokens = self.ntk.get_tokens_cleaned(self.doc)
        ngrams = self.ntk.get_ngrams()
        self.assertEqual(ngrams, [])
        ngrams = self.ntk.get_ngrams(degree = 1, tokens = tokens)
        self.assertEqual(type(ngrams[0]), tuple)
        ngrams = self.ntk.get_ngrams(degree = 1, doc = self.doc)
        self.assertEqual(type(ngrams[0]), tuple)
        ngrams = self.ntk.get_ngrams(degree = 1, doc = self.doc, is_tuple = False)
        np.testing.assert_array_equal(ngrams, tokens)

    def test_get_ngrams_features(self):
        tokens = self.ntk_no_stop_words.get_tokens_cleaned(self.doc, is_lemma = False)
        features = self.ntk_no_stop_words.get_ngrams_features()
        self.assertEqual(features, {})
        tokens_features = self.ntk_no_stop_words.get_ngrams_features(degree = 1, tokens = tokens)
        self.assertEqual(tokens_features, {'good': 1, 'case': 1, 'excellent': 1, 'value': 1, 'i': 1, 'am': 1, 'agree': 1, 'there': 1, 'is': 1, 'a': 1, 'mistake': 1, 'item': 1, 'does': 1, 'not': 1, 'match': 1, 'picture': 1})
        doc_features = self.ntk_no_stop_words.get_ngrams_features(degree = 1, doc = self.doc)
        self.assertEqual(doc_features, tokens_features)
        features = self.ntk_no_stop_words.get_ngrams_features(degree = 1, doc = self.doc, is_lemma = True)
        self.assertEqual(features, {'good': 1, 'case': 1, 'excellent': 1, 'value': 1, 'i': 1, 'be': 1, 'agree': 1, 'there': 1, 'a': 1, 'mistake': 1, 'item': 1, 'do': 1, 'not': 1, 'match': 1, 'picture': 1})

    def test_create_ngrams_features_from_docs(self):
        features = self.ntk.create_ngrams_features_from_docs(self.docs, True)
        self.assertEqual(type(features[0]), tuple)
        self.assertEqual(features[0][1], True)
        self.assertEqual(features[1][0], {})

    def test_create_ngrams_features_from_tuples(self):
        features = self.ntk.create_ngrams_features_from_tuples(self.tuples, True)
        self.assertEqual(type(features[0]), tuple)
        self.assertEqual(features[0][1], True)
        self.assertEqual(features[1][0], {})

    def test_get_features(self):
        features = self.ntk.get_features(self.docs[0])
        self.assertEqual(features, {'words_top': 0, 'neg': 0.0, 'neu': 0.1, 'pos': 0.9, 'compound': 0.8402})
        features = self.ntk_no_stop_words.get_features(self.docs[1], is_lemma = True, degree = 1)
        self.assertEqual(features, {'words_top': 0, 'i': 1, 'be': 1, 'agree': 1, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612})
        features = self.ntk_no_stop_words.get_features(self.docs[1], is_lemma = False, degree = 1)
        self.assertEqual(features, {'words_top': 0, 'i': 1, 'am': 1, 'agree': 1, 'neg': 0.0, 'neu': 0.286, 'pos': 0.714, 'compound': 0.3612})

    def create_words_map(self):
        tokens = self.ntk.get_tokens_cleaned(self.doc)
        return self.ntk.create_words_map(tokens)

    def test_create_words_map(self):
        words_map = self.create_words_map()
        self.assertEqual(words_map, self.default_doc_filtered)

    def test_create_words_cloud(self):
        words_map = self.create_words_map()
        words_cloud = self.ntk.create_words_cloud(words_map, True)
        np.testing.assert_array_equal(words_cloud.words_, {'good': 1.0, 'case': 1.0, 'excellent': 1.0, 'value': 1.0, 'agree': 1.0, 'mistake': 1.0, 'item': 1.0, 'match': 1.0, 'picture': 1.0})

    def test_vectorize_docs(self):
        data = pd.DataFrame(self.docs, columns=['text'])
        features = self.ntk.get_features_from_docs(self.docs)
        features_df = pd.DataFrame.from_dict(features, orient='columns')
        data = pd.concat([data, features_df], axis='columns')
        features_mix = data[['text', 'words_top', 'neg', 'neu', 'pos', 'compound']].to_dict(orient="records")

        X_train_dict = self.ntk.vectorize_docs(features_mix)
        self.assertEqual(type(X_train_dict[0]), scipy.sparse.csr.csr_matrix)
        vectorizer_dict = self.ntk.vectorizer
        self.assertEqual(len(vectorizer_dict.vocabulary_), 9)
        X_test_dict = self.ntk.vectorize_docs(features_mix, is_test = True)
        self.assertEqual(type(X_test_dict[0]), scipy.sparse.csr.csr_matrix)

        X_train_count = self.ntk.vectorize_docs(self.docs)
        self.assertEqual(type(X_train_count[0]), scipy.sparse.csr.csr_matrix)
        vectorizer_count = self.ntk.vectorizer
        self.assertEqual(len(vectorizer_count.vocabulary_), 14)
        X_test_count = self.ntk.vectorize_docs(self.docs, is_test = True)
        self.assertEqual(type(X_test_count[0]), scipy.sparse.csr.csr_matrix)

        X_train_tfidf = self.ntk.vectorize_docs(self.docs, False)
        self.assertEqual(type(X_train_tfidf[0]), scipy.sparse.csr.csr_matrix)
        vectorizer_tfidf = self.ntk.vectorizer
        self.assertEqual(len(vectorizer_tfidf.vocabulary_), 14)
        X_test_tfidf = self.ntk.vectorize_docs(self.docs, is_test = True)
        self.assertEqual(type(X_test_tfidf[0]), scipy.sparse.csr.csr_matrix)

        X_train_count = self.ntk.vectorize_docs(self.docs, is_lemma = True)
        self.assertEqual(type(X_train_count[0]), scipy.sparse.csr.csr_matrix)
        vectorizer_lemma = self.ntk.vectorizer
        self.assertEqual(len(vectorizer_lemma.vocabulary_), 9)

        X_train_tfidf = self.ntk.vectorize_docs(self.docs, is_count = False, is_lemma = True)
        self.assertEqual(type(X_train_tfidf[0]), scipy.sparse.csr.csr_matrix)
        vectorizer_lemma = self.ntk.vectorizer
        self.assertEqual(len(vectorizer_lemma.vocabulary_), 9)

if __name__ == '__main__':
    unittest.main()