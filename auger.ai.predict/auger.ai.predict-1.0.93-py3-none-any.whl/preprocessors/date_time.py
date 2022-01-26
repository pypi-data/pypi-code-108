from auger_ml.preprocessors.base import BasePreprocessor

import pandas as pd
import numpy as np
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)


class DateTimePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(DateTimePreprocessor, self).__init__(
            params=params,
            params_keys=['datetime_cols', 'discover_fields']
        )
        self._initial_datetime_cols = params.get('datetime_cols', [])
        self._discover_fields = params.get('discover_fields', True)

    @staticmethod
    def _extract_features(df, col):
        df["cyclic__" + col.name + "__minute"] = 2 * np.pi * col.dt.minute / 60
        df["cyclic__" + col.name + "__hour"] = 2 * np.pi * col.dt.hour / 24
        df["cyclic__" + col.name + "__mday"] = 2 * np.pi * (col.dt.day - 1) / 30
        df["cat__" + col.name + "__wday"] = col.dt.weekday
        df["cyclic__" + col.name + "__yday"] = 2 * np.pi * col.dt.dayofyear / 365
        df["cat__" + col.name + "__month"] = col.dt.month
        df[col.name + "__year"] = col.dt.year

    def fit(self, df):
        from pandas.api.types import is_datetime64_any_dtype as is_datetime

        super(DateTimePreprocessor, self).fit(df)

        self._datetime_cols = self._initial_datetime_cols
        if self._discover_fields:
            for column in df.columns:
                if is_datetime(df[column]):
                    self._datetime_cols.append(column)

        for col in self._datetime_cols:
            if col not in df.columns:
                self._datetime_cols.remove(col)

        self._datetime_cols = list(set(self._datetime_cols))

    def transform(self, df):
        super(DateTimePreprocessor, self).transform(df)

        for c in self._datetime_cols:
            #df = pd.concat([df, self._extract_features(df[c])], axis=1).drop(c, axis=1)
            if not 'datetime64' in str(df[c].dtype):
                if df[c].dtype == 'object':
                    value = pd.to_datetime(df[c], infer_datetime_format=True, errors='ignore', utc=True)
                else:
                    value = pd.to_datetime(df[c], unit='s') #TODO : support ns

                self._extract_features(df, value)
            else:
                self._extract_features(df, df[c])

            df.drop(c, axis=1, inplace=True)

        return df
