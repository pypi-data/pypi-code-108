import numpy as np

import sklearn.linear_model

class PassiveAggressiveClassifier(sklearn.linear_model.PassiveAggressiveClassifier):
    def predict_proba(self, x):
        raw_scores = self.decision_function(x)

        if len(raw_scores.shape) == 1:
            new_scores = np.zeros((raw_scores.shape[0], 2))
            new_scores[:, 0] = -raw_scores
            new_scores[:, 1] = raw_scores
            raw_scores = new_scores

        if not hasattr(self, '__platt'):
            platt_predictions = 1 / (1 + np.exp(raw_scores))
        else:
            platt_predictions = self.__platt(raw_scores)

        return (1. - platt_predictions) / platt_predictions.sum(axis=1)[:, None]

class Perceptron(sklearn.linear_model.Perceptron):
    def predict_proba(self, x):
        raw_scores = self.decision_function(x)

        if len(raw_scores.shape) == 1:
            new_scores = np.zeros((raw_scores.shape[0], 2))
            new_scores[:, 0] = -raw_scores
            new_scores[:, 1] = raw_scores
            raw_scores = new_scores

        if not hasattr(self, '__platt'):
            platt_predictions = 1 / (1 + np.exp(raw_scores))
        else:
            platt_predictions = self.__platt(raw_scores)

        return (1. - platt_predictions) / platt_predictions.sum(axis=1)[:, None]
