from auger_ml.preprocessors.base import BasePreprocessor


class InterpolatePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(InterpolatePreprocessor, self).__init__(
            params=params,
            params_keys=['method']
        )
        self._method = params.get('method', 'pad')

    def fit(self, df):
        super(InterpolatePreprocessor, self).fit(df)

    def transform(self, df):
        super(InterpolatePreprocessor, self).transform(df)

        df = df.interpolate(method=self._method, limit_direction='forward')

        return df
