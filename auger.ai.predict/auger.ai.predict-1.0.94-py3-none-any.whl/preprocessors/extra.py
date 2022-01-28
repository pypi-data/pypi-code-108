import numpy as np

from auger_ml.preprocessors.base import BasePreprocessor


class ExtraPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(ExtraPreprocessor, self).__init__(
            params=params,
            params_keys=['cyclic_cols', 'interaction_cols']
        )
        self._initial_cyclic_cols = params.get('cyclic_cols', [])
        self._interaction_cols = params.get('interaction_cols', [])

    def _cyclic(self, df):
        for c in self._cyclic_cols:
            df[c + "_sin"] = np.sin(df[c])
            df[c + "_cos"] = np.cos(df[c])

        df.drop(self._cyclic_cols, axis=1, inplace=True)

    def _interaction(self, df):
        for i in range(len(self._interaction_cols)):
            for j in range(i + 1, len(self._interaction_cols)):
                df["m__" + self._interaction_cols[i] + "_" + self._interaction_cols[j]] = \
                    df[self._interaction_cols[i]] * df[self._interaction_cols[j]]

    def fit(self, df):
        super(ExtraPreprocessor, self).fit(df)

        self._cyclic_cols = self._initial_cyclic_cols[:]
        # add implicit cyclic columns
        for c in df.columns:
            if c.startswith("cyclic__"):
                self._cyclic_cols.append(c)

    def transform(self, df):
        super(ExtraPreprocessor, self).transform(df)

        self._cyclic(df)
        self._interaction(df)

        return df
