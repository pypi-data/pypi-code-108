################################################################################
# Licensed Materials - Property of IBM
# SVL720190128
# (C) Copyright IBM Corp. 2019-2020
################################################################################
# common imports
import numpy as np
import pandas as pd
import logging

from sklearn.base import BaseEstimator

logger = logging.getLogger()


class SmallDataWindowTransformer(BaseEstimator):
    def __init__(self, lookback_window=None, cache_last_window_trainset=False):
        self.lookback_window = lookback_window
        self.cache_last_window_trainset = cache_last_window_trainset
        self.X_train_last_window_ = None

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        if self.lookback_window is None:
            # calculate lookback_window
            if X.shape[1] > 5:
                self.lookback_window = 20
            else:
                self.lookback_window = 30

        if self.cache_last_window_trainset:  # keep the last lookback window of train set
            if self.lookback_window < X.shape[0]:
                self.X_train_last_window_ = X[-self.lookback_window:, ]
            else:
                self.X_train_last_window_ = X

        return self

    # X is the raw timeseries data
    def transform(self, X):
        # Check if this is train time or test time
        test_len = -1
        if self.cache_last_window_trainset:
            if (X.shape[0] < self.lookback_window)\
                    or (not np.array_equal(X[-self.lookback_window:, ], self.X_train_last_window_)):  # test time
                # TODO: what if the train set is smaller than the self.lookback_window
                test_len = X.shape[0]
                # prepend cached last lookback window of train set to test set
                X = np.concatenate((self.X_train_last_window_, X), axis=0)

        datadf = pd.DataFrame(X)
        cols_X = []
        # input sequence (t-n, ... t-1)
        for i in range(self.lookback_window - 1, 0, -1):
            cols_X.append(datadf.shift(i))

        cols_X.append(datadf)
        dfX = pd.concat(cols_X, axis=1)
        Xt = dfX.values
        if test_len > 0:  # this is test time, remove cached lookback window data to get back the test set
            Xt = Xt[-test_len:, ]

        return Xt


class SmallDataWindowTargetTransformer(BaseEstimator):
    def __init__(self, prediction_horizon):
        self.prediction_horizon = prediction_horizon

    # do nothing in fit
    def fit(self, X: np.ndarray, y: np.ndarray = None):
        return self

    # X is the raw timeseries target
    def transform(self, X: np.ndarray) -> np.ndarray:
        # Note: X here is the target we need to transform
        targetdf = pd.DataFrame(X)
        cols = list()
        for i in range(1, self.prediction_horizon+1):
            cols.append(targetdf.shift(-i))

        dfY = pd.concat(cols, axis=1)
        return dfY.values