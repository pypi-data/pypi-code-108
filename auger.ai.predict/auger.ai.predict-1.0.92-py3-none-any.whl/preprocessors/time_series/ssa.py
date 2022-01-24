from auger_ml.preprocessors.base import BasePreprocessor

from sklearn.decomposition import PCA

import pandas as pd
import numpy as np


class SSAPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(SSAPreprocessor, self).__init__(
            params=params,
            params_keys=['lag_length', 'n_components']
        )

        self._lag_length = params.get('lag_length', 10)
        self._n_components = params.get('n_components', 5)

    @staticmethod
    def _ssa(ts, lag_length, n_components):
        # align embedding dimension with lag length
        if lag_length - n_components % 2 != 0:
            lag_length += 1

        # create lag matrix
        lag_matrix = pd.concat([ts.shift(i) for i in range(lag_length)], axis=1).dropna()

        # do PCA
        lag_matrix = PCA(n_components).fit_transform(lag_matrix)

        # restore time series
        ts = [lag_matrix.diagonal(i).mean() for i in range(n_components - 1, lag_length - len(ts) - 1, -1)]

        # do padding
        pad_len = (lag_length - n_components) // 2
        ts = [ts[0]] * pad_len + ts + [ts[-1]] * pad_len

        return np.squeeze(ts)

    def fit(self, df):
        super(SSAPreprocessor, self).fit(df)

    def transform(self, df):
        super(SSAPreprocessor, self).transform(df)

        assert len(df.columns.values) == 1

        res = pd.DataFrame({df.columns[0]: self._ssa(df.iloc[:, 0], self._lag_length, self._n_components)},
                           index=df.index)

        return res
