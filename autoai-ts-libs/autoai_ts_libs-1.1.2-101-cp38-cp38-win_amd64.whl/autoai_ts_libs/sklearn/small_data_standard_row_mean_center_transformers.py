import numpy as np
from numpy.random import default_rng
import pandas as pd
import logging

from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer
from autoai_ts_libs.utils.messages.messages import Messages

logger = logging.getLogger()


class WindowTransformerMTS(BaseEstimator):
    def __init__(self, lookback_window=None, prediction_horizon=1):
        self.lookback_window = lookback_window
        self.prediction_horizon = prediction_horizon

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        return self

    # X: raw time series
    def transform(self, X, y=None):
        X_ret, y_ret = None, None
        # for each time series in the MTS raw time series X
        for i in range(X.shape[1]):
            Xt = self.transform_feature_(X=X[:, i])
            df = pd.DataFrame(Xt)

            if y is not None:  # fit time
                yt = self.transform_target_(X=y[: , i])
                df['target'] = yt
                df.dropna(inplace=True)
                Xt = df.values[:, :-1]
                yt = df['target']
                yt = np.array(yt, dtype=np.float64).reshape(-1, 1)
            else:  # predict time
                if df.isnull().values.any():
                    si = SimpleImputer()
                    X2 = si.fit_transform(X=df.values)
                    df = pd.DataFrame(X2)
                Xt = df.values
                yt = None

            Xt = np.array(Xt, dtype=np.float64)
            # appended the last column
            if X_ret is None:
                X_ret = Xt
            else:
                X_ret = np.concatenate((X_ret, Xt), axis=1)

            # appended the last column
            if y_ret is None:
                y_ret = yt
            else:
                y_ret = np.concatenate((y_ret, yt), axis=1)

        return X_ret, y_ret

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X, y)

    def transform_feature_(self, X):
        if self.lookback_window is None:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0008E'))

        datadf = pd.DataFrame(X)
        cols_X = []
        # input sequence (t-n, ... t-1)
        for i in range(self.lookback_window - 1, 0, -1):
            cols_X.append(datadf.shift(i))

        cols_X.append(datadf)
        dfX = pd.concat(cols_X, axis=1)
        Xt = dfX.values

        return Xt

    def transform_target_(self, X):
        # Note: X here is the target we need to transform
        targetdf = pd.DataFrame(X)
        cols = list()
        for i in range(1, self.prediction_horizon + 1):
            cols.append(targetdf.shift(-i))

        dfY = pd.concat(cols, axis=1)
        return dfY.values


class StandardRowMeanCenterMTS(BaseEstimator):
    def __init__(self, lookback_window=None, random_state=42):
        self.lookback_window = lookback_window
        self.transformers = list()
        if self.lookback_window is None:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0008E'))
        self.random_state = random_state
        self.rng = default_rng(random_state)

    # X: windowed data
    def fit(self, X: np.ndarray, y: np.ndarray = None):
        num_ts = int(X.shape[1] / self.lookback_window)  # number of actual time series
        for i in range(num_ts):
            self.transformers.append(StandardRowMeanCenter(random_state=self.rng.integers(1e6)))

        return self

    # X: windowed data
    def transform(self, X, y=None):
        num_ts = int(X.shape[1] / self.lookback_window)  # number of actual time series

        # keep transformed space
        X_ret, y_ret = None, None
        for i in range(num_ts):
            # get windowed data for i_th time series
            Xi = X[:, i * self.lookback_window: (i+1) * self.lookback_window]
            if y is not None:
                (Xt, yt) = self.transformers[i].fit_transform(X=Xi, y=y[:, i].reshape(-1, 1))
            else:
                (Xt, yt) = self.transformers[i].fit_transform(X=Xi)

            # appended the last column
            if X_ret is None:
                X_ret = Xt
            else:
                X_ret = np.concatenate((X_ret, Xt), axis=1)

            # appended the last column
            if y_ret is None:
                y_ret = yt
            else:
                y_ret = np.concatenate((y_ret, yt), axis=1)

        return X_ret, y_ret

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X, y)

    def inverse_transform(self, y):
        if self.transformers is None:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0009E'))

        if y is None:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0010E'))

        if y.ndim == 1:
            y = y.reshape(-1, 1)

        y_inv_ret = None
        # go through each time series, y is in transformed space
        for i in range(y.shape[1]):
            y_inv = self.transformers[i].inverse_transform(y=y[:, i])

            # appended the last column
            if y_inv_ret is None:
                y_inv_ret = y_inv
            else:
                y_inv_ret = np.concatenate((y_inv_ret, y_inv), axis=1)

        return y_inv_ret


class StandardRowMeanCenter(BaseEstimator):
    
    def __init__(self, add_noise=True, noise_var=1E-5, random_state=42):
        self.noise_var = noise_var
        self.add_noise = add_noise
        self.random_state = random_state
        self.rng = default_rng(random_state)

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        self.X_mu = np.mean(X, axis=1).reshape(-1, 1)
        self.X_std = np.std(X, axis=1).reshape(-1, 1)
        self.zero_std_idx = np.where(self.X_std == 0.0)[0]
        # print("* " * 30)
        # print("self.zero_std_idx", self.zero_std_idx)
        self.X_std[self.zero_std_idx] = 1.0

    def transform(self, X, y=None):
        X_tr = np.divide(X - self.X_mu, self.X_std)
        if self.add_noise:
            if len(self.zero_std_idx) > 0:
                # zm_noise = np.random.normal(0, self.noise_var, size=(len(self.zero_std_idx), X.shape[1]))
                zm_noise = self.rng.normal(0, self.noise_var, size=(len(self.zero_std_idx), X.shape[1]))
                X_tr[self.zero_std_idx, :] = zm_noise
        if y is not None:
            y_tr = np.divide(y - self.X_mu, self.X_std)
            return X_tr, y_tr
        else:
            return X_tr, None

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X, y)
        
    def inverse_transform(self, y):
        y_inv = np.multiply(y.reshape(-1, 1), self.X_std) + self.X_mu
        return y_inv

# Input: univariate time series T
# Output: StandardRowMeanCentered X and y
class WindowStandardRowMeanCenterUTS(BaseEstimator):
    def __init__(self, lookback_window=10, prediction_horizon=1, random_state=42):
        self.lookback_window = lookback_window
        self.prediction_horizon = prediction_horizon
        self.random_state = random_state
        self.row_transformer = StandardRowMeanCenter(random_state=random_state)

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        return self

    def transform(self, X, y=None):
        Xt = self.transform_(X=X)
        df = pd.DataFrame(Xt)

        if y is not None:
            yt = self.transform_target_(X=y)
            df['target'] = yt

        if y is not None:  # fit time
            df.dropna(inplace=True)
        else:  # predict time
            if df.isnull().values.any():
                si = SimpleImputer()
                X2 = si.fit_transform(X=df.values)
                df = pd.DataFrame(X2)

        if y is not None:
            Xt = df.values[:, :-1]
            yt = df['target']
            yt = np.array(yt, dtype=np.float64).reshape(-1, 1)
        else:
            Xt = df.values
            yt = None

        Xt = np.array(Xt, dtype=np.float64)
        (Xt, yt) = self.row_transformer.fit_transform(X=Xt, y=yt)
        return Xt, yt

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X, y)

    def inverse_transform(self, y):
        y_inv = self.row_transformer.inverse_transform(y=y)
        return y_inv

    def transform_(self, X):
        datadf = pd.DataFrame(X)
        cols_X = []
        # input sequence (t-n, ... t-1)
        for i in range(self.lookback_window - 1, 0, -1):
            cols_X.append(datadf.shift(i))

        cols_X.append(datadf)
        dfX = pd.concat(cols_X, axis=1)
        Xt = dfX.values

        return Xt

    def transform_target_(self, X):
        # Note: X here is the target we need to transform
        targetdf = pd.DataFrame(X)
        cols = list()
        for i in range(1, self.prediction_horizon + 1):
            cols.append(targetdf.shift(-i))

        dfY = pd.concat(cols, axis=1)
        return dfY.values


# Input: multivariate time series T
# Output: StandardRowMeanCentered X and y
class WindowStandardRowMeanCenterMTS(BaseEstimator):
    def __init__(self, lookback_window=10, prediction_horizon=1, random_state=42):
        self.lookback_window = lookback_window
        self.prediction_horizon = prediction_horizon
        self.row_transformers = None
        self.random_state = random_state
        self.rng = default_rng(random_state)

    def fit(self, X, y=None):
        self.row_transformers = list()
        for i in range(X.shape[1]):
            row_transformer = WindowStandardRowMeanCenterUTS(lookback_window=self.lookback_window,
                                                             prediction_horizon=self.prediction_horizon,
                                                             random_state=self.rng.integers(1e6))
            self.row_transformers.append(row_transformer)

        return self

    def transform(self, X, y=None):
        if self.row_transformers is None:
            print('ERROR: row_transformers is None')
            return X, y
        if X is not None and X.ndim == 1:
            X = X.reshape(-1, 1)
        if y is not None and y.ndim == 1:
            y = y.reshape(-1, 1)

        X_tr, y_tr = None, None
        for i in range(X.shape[1]):
            if y is not None:
                (Xt, yt) = self.row_transformers[i].fit_transform(X=X[:, i], y=y[:, i])
            else:
                (Xt, yt) = self.row_transformers[i].fit_transform(X=X[:, i])

            if X_tr is None:
                X_tr = Xt
            else:
                X_tr = np.concatenate((X_tr, Xt), axis=1)
            if y_tr is None:
                y_tr = yt
            else:
                y_tr = np.concatenate((y_tr, yt), axis=1)

        return X_tr, y_tr

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X, y)

    def inverse_transform(self, y):
        if self.row_transformers is None:
            print('ERROR: row_transformers is None')
            return y

        if y is None:
            print('ERROR: y is None')
            return y

        if y.ndim == 1:
            y = y.reshape(-1, 1)

        y_inv_ret = None
        for i in range(y.shape[1]):
            y_inv = self.row_transformers[i].inverse_transform(y=y[:, i])
            if y_inv_ret is None:
                y_inv_ret = y_inv
            else:
                y_inv_ret = np.concatenate((y_inv_ret, y_inv), axis=1)

        return y_inv_ret


if __name__ == '__main__':
    lookback_window = 12
    window_transformer = WindowTransformerMTS(lookback_window=lookback_window)
    rowmean_transformer = StandardRowMeanCenterMTS(lookback_window=lookback_window)

    df = pd.read_csv('~/bm4autoai/data/srom-data/univariate/AirPassengers.csv')
    trainsize = 100
    X = df.values[:, 1][:trainsize].reshape(-1, 1)
    y = df.values[:, 1][:trainsize].reshape(-1, 1)

    (Xw, yw) = window_transformer.fit_transform(X, y)
    (X, y) = rowmean_transformer.fit_transform(Xw, yw)
