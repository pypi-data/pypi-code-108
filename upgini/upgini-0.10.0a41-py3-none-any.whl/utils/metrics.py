import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score


def accuracy100(target, predictions):
    result = 100 * accuracy_score(target, predictions)
    if np.isnan(result):
        result = 0
    return result


def gini(target, predictions):
    return 100 * (2 * roc_auc_score(target, predictions) - 1)
