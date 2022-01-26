from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.vector_ar.var_model import VAR

from sklearn.base import BaseEstimator

import numpy as np


class ARIMAXBaseRegressor(BaseEstimator):
    def __init__(self, p=1, d=1, q=1):
        self._p = p
        self._d = d
        self._q = q

        self._estimator = None

    def fit(self, X, y):
        if isinstance(X, tuple):
            X, _ = X

        self._estimator = ARIMA(y, (self._p, self._d, self._q), exog=X.astype(float)).fit(disp=-1)
        return self

    def predict(self, X):
        if self._estimator is None:
            raise ValueError("Estimator is not fitted")

        if isinstance(X, tuple):
            X, y, _ = X
        else:
            y = X[:, -1]
            X = X[:, :-1]

        return self._estimator.forecast(steps=len(y), exog=X.astype(float))[0]

    def get_params(self, deep=True):
        return {"p": self._p, "d": self._d, "q": self._q}


class VARXBaseRegressor(BaseEstimator):
    def __init__(self, maxlag=5):
        self._maxlag = maxlag

        self._estimator = None
        self._prior_values = None

    def fit(self, X, y):
        if isinstance(X, tuple):
            X, _ = X

        X["target"] = y

        self._estimator = VAR(X.astype(float), exog=None).fit(self._maxlag)
        self._prior_values = np.array(X[-self._maxlag:])

        return self

    def predict(self, X=None):
        if self._estimator is None:
            raise ValueError("Estimator is not fitted")

        if isinstance(X, tuple):
            X, y, _ = X

        return self._estimator.forecast(self._prior_values, steps=len(X), exog_future=None)[:, -1]

    def get_params(self, deep=True):
        return {"maxlab": self._maxlag}
