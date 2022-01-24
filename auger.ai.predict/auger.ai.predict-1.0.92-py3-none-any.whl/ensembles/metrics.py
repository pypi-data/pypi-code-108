import numpy as np
from sklearn.metrics import *


def neg_log_loss(y_true, y_pred):
    return -log_loss(y_true, y_pred)


# =============== Regression Scores ===============

def neg_mean_squared_error_score(y_true, y_pred):
    return -mean_squared_error(y_true, y_pred)


def neg_mean_squared_log_error_score(y_true, y_pred):
    return -mean_squared_log_error(y_true, y_pred)


def neg_mean_absolute_error_score(y_true, y_pred):
    return -mean_absolute_error(y_true, y_pred)


def neg_median_absolute_error_score(y_true, y_pred):
    return -median_absolute_error(y_true, y_pred)

def normalized_mean_absolute_error_score(y_true, y_pred):
    """ Normalized Root Mean Squared Error """
    return mean_absolute_error(y_true, y_pred) / (y_true.max() - y_true.min())

def normalized_root_mean_squared_error_score(y_true, y_pred):
    """ Normalized Root Mean Squared Error """
    return np.sqrt(mean_squared_error(y_true, y_pred)) / (y_true.max() - y_true.min())

def spearman_correlation_score(y_true, y_pred):
    from scipy import stats

    return stats.spearmanr(y_true, y_pred)[0]

def norm_macro_recall_score(y_true, y_pred):
    R = 0.5 #TODO: support multiclass R=(1/C) for C-class classification problems
    return (recall_macro(y_true, y_pred) - R)/(1 - R)

def average_precision_score_weighted_score(y_true, y_pred):
    return average_precision_score(y_true, y_pred, average='weighted')
