from auger_ml.preprocessors.base import BasePreprocessor

import pandas as pd
import numpy as np


class EmbeddingPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(EmbeddingPreprocessor, self).__init__(
            params=params,
            params_keys=['embedding_dim'],
        )

        self._embedding_dim = params.get('embedding_dim', 2)

    def fit(self, df):
        super(EmbeddingPreprocessor, self).fit(df)

    def transform(self, df):
        super(EmbeddingPreprocessor, self).transform(df)

        s = df.squeeze()

        if len(s) < self._embedding_dim:
            raise ValueError("Data size must be not less than embedding dimension(%s, %s)"%(len(s), self._embedding_dim))

        # add one more value for prediction
        horizon = s.index[1] - s.index[0]
        s = s.append(pd.Series([np.nan], index=[s.index[-1] + horizon], name=s.name))

        df = pd.DataFrame(pd.concat([s.shift(i).rename(s.name if i == 0 else s.name + "_" + str(i))
                                     for i in range(self._embedding_dim)], axis=1), index=s.index)
        df = df.iloc[self._embedding_dim:]

        # TODO: remove after fixing training with NA
        df = df.dropna()

        return df.iloc[:, 1:], df.iloc[:, 0]  # features, target
