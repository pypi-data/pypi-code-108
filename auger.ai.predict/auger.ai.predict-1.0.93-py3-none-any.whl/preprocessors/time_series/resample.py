from auger_ml.preprocessors.base import BasePreprocessor

import pandas as pd


class ResamplePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(ResamplePreprocessor, self).__init__(
            params=params,
            params_keys=['datetime_col', 'sample_rate', 'window_size']
        )

        self._datetime_col = params.get('datetime_col', None)
        self._sample_rate = params.get('sample_rate', None)
        self._window_size = params.get('window_size', 1)

    # def _infer_sample_rate(self, df):
    #     sample_rate = df[self._datetime_col].diff().median()
    #     return sample_rate

    def fit(self, df):
        super(ResamplePreprocessor, self).fit(df)

        # df[self._datetime_col] = pd.to_datetime(df[self._datetime_col])
        #
        # if self._datetime_col is not None:
        #     if self._sample_rate is None:
        #         self._sample_rate = self._infer_sample_rate(df)

    def transform(self, df):
        super(ResamplePreprocessor, self).transform(df)

        if self._datetime_col is not None:
            df = df.set_index(self._datetime_col). \
                resample(self._sample_rate).mean(). \
                rolling(self._window_size, min_periods=1).mean()

        return df
