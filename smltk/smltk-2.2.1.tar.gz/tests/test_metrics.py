import unittest
from smltk.metrics import Metrics
from smltk.preprocessing import Ntk
import nltk
import numpy as np
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
import os

class TestMetrics(unittest.TestCase, Metrics):
    mtr = None
    ntk = None
    doc = 'Good case, Excellent value. I am agree. There is a mistake. Item Does Not Match Picture.'
    docs = []
    target = []
    tuples = []
    def __init__(self, *args, **kwargs):
        self.mtr = Metrics()
        self.ntk = Ntk()
        self.docs = nltk.sent_tokenize(self.doc)
        self.target = [1, 1, 0, 0]
        self.tuples = self.ntk.create_tuples(self.docs, self.target)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def training(self):
        features_lemma = self.ntk.create_features_from_tuples(self.tuples, True)
        classifier = nltk.NaiveBayesClassifier.train(features_lemma)
        return classifier, features_lemma

    def prediction(self):
        classifier, features_lemma = self.training()
        y_test, y_pred = self.mtr.prediction(classifier, 'classify', features_lemma)
        return y_test, y_pred

    def test_split_tuples(self):
        classifier, features_lemma = self.training()
        X_test, y_test = self.split_tuples(features_lemma)
        self.assertEqual(y_test, [1, 1, 0, 0])

    def test_prediction(self):
        classifier, features_lemma = self.training()
        y_test, y_pred = self.mtr.prediction(classifier, 'classify', features_lemma)
        self.assertEqual(y_test, y_pred)
        y_test, y_pred = self.mtr.prediction(classifier, 'classify', [])
        self.assertEqual(y_test, y_pred)
        np.testing.assert_array_equal(y_pred, [])
        X_test = pd.Series(features_lemma)
        y_test, y_pred = self.mtr.prediction(classifier, 'classify', X_test)
        self.assertEqual(y_test, y_pred)

    def test_create_confusion_matrix(self):
        y_test, y_pred = self.prediction()
        np.testing.assert_array_equal(self.mtr.create_confusion_matrix(y_test, y_pred, True), [[2, 0], [0, 2]])

    def test_is_binary_classification(self):
        y_test = [1, 0, 1]
        y_pred = [0, 1, 0]
        self.assertTrue(self.mtr.is_binary_classification(y_test, y_pred))
        y_pred = [0, 1, 2]
        self.assertFalse(self.mtr.is_binary_classification(y_test, y_pred))

    def test_clean_binary_classification(self):
        y_test = [1, 0, 1]
        y_pred = [0, 1, 0]
        y_test_cleaned, y_pred_cleaned = self.mtr.clean_binary_classification(y_test, y_pred)
        self.assertEqual(y_test_cleaned[0], 1)
        self.assertEqual(y_test_cleaned[1], 0)
        self.assertEqual(y_pred_cleaned[0], 0)
        self.assertEqual(y_pred_cleaned[1], 1)
        y_test = ['pos', 'neg', 'pos']
        y_pred = ['neg', 'pos', 'neg']
        y_test_cleaned, y_pred_cleaned = self.mtr.clean_binary_classification(y_test, y_pred)
        self.assertEqual(y_test_cleaned[0], 1)
        self.assertEqual(y_test_cleaned[1], 0)
        self.assertEqual(y_pred_cleaned[0], 0)
        self.assertEqual(y_pred_cleaned[1], 1)

    def test_get_classification_metrics(self):
        classifier, features_lemma = self.training()
        y_test, y_pred = self.mtr.prediction(classifier, 'classify', features_lemma)
        X_test, y_test = self.mtr.split_tuples(features_lemma)
        params = {
            "model": classifier,
            "X_train": np.array(X_test),
            "y_train": np.array(y_test),
            "X_test": np.array(X_test),
            "y_test": np.array(y_test),
            "y_pred": y_pred
        }
        metrics = self.mtr.get_classification_metrics(params)
        self.assertEqual(metrics['Loss'], 0)
        self.assertEqual(metrics['Accuracy'], 1.0)
        self.assertEqual(metrics['MCC'], 1.0)
        self.assertEqual(metrics['ROC_AUC'], 1.0)
        np.testing.assert_array_equal(metrics['Precision'], [1., 1.])
        np.testing.assert_array_equal(metrics['Support'], [2, 2])
        params = {
            "y_test": np.array(y_test),
            "y_pred": y_pred
        }
        metrics = self.mtr.get_classification_metrics(params)
        self.assertEqual(metrics['Loss'], 0)
        self.assertEqual(metrics['Accuracy'], 1.0)
        self.assertEqual(metrics['MCC'], 1.0)
        self.assertEqual(metrics['ROC_AUC'], 1.0)
        np.testing.assert_array_equal(metrics['Precision'], [1., 1.])
        np.testing.assert_array_equal(metrics['Support'], [2, 2])

        data = load_wine()
        X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=5)
        model = SGDClassifier(random_state=3)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        params = {
            "model": model,
            "X_train": np.array(X_train),
            "y_train": np.array(y_train),
            "X_test": np.array(X_test),
            "y_test": np.array(y_test),
            "y_pred": y_pred
        }
        metrics = self.mtr.get_classification_metrics(params)
        self.assertEqual(metrics['Loss'], 0.7443055555555557)
        self.assertEqual(metrics['Accuracy'], 0.6666666666666666)
        self.assertEqual(metrics['MCC'], 0.4802259242337604)
        np.testing.assert_array_equal(metrics['Precision'][2], 0.4)
        np.testing.assert_array_equal(metrics['Support'][2], 8)

    def test_scoring(self):
        data = load_wine()
        X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=5)
        model = SGDClassifier(random_state=3)
        model.fit(X_train, y_train)
        metrics = self.mtr.scoring(model, X_test, y_test)
        self.assertEqual(metrics['Accuracy'], 0.6666666666666666)

    def test_modeling(self):
        data = load_wine()
        X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=5)
        model = SGDClassifier(random_state=3)
        metrics = self.mtr.modeling(model, X_train, y_train, X_test, y_test)
        self.assertEqual(metrics['Accuracy'], 0.6666666666666666)

    def test_manage_model(self):
        filename = '/tmp/save.model'
        classifier, features_lemma = self.training()
        y_test1, y_pred1 = self.mtr.prediction(classifier, 'classify', features_lemma)
        self.mtr.save_model(classifier, filename)
        self.assertFalse(os.stat(filename).st_size == 0)
        model = self.mtr.resume_model(filename)
        y_test2, y_pred2 = self.mtr.prediction(model, 'classify', features_lemma)
        self.assertEqual(y_test1, y_test2)
        self.assertEqual(y_pred1, y_pred2)

if __name__ == '__main__':
    unittest.main()