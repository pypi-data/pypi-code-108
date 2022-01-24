from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge, LinearRegression

from pandas.api.types import is_numeric_dtype

from auger_ml.preprocessors.base import BasePreprocessor


DATASET_SIZE_THRESHOLDS = {
    (1, 10**3): RandomForestRegressor,
    (10**3 + 1, 10**5): BayesianRidge,
    (10**5 + 1, 10**6): LinearRegression,
    (10**6 + 1, 10**10): None
}


class NanPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(NanPreprocessor, self).__init__(
            params=params,
            params_keys=['thresh_col', 'thresh_row']
        )

        self._thresh_col = params.get('thresh_col', 0.95)
        self._thresh_row = params.get('thresh_row', 0.05)
        self._imputer_rounds = params.get('imputer_rounds', 10)
        self._use_iterative_imputer = False

    def fit(self, df):
        super(NanPreprocessor, self).fit(df)

        self._cols_to_drop = [c for c in df.columns if df[c].isna().mean() > self._thresh_col]
        self._numeric_cols = [c for c in df.columns if is_numeric_dtype(df[c]) and c not in self._cols_to_drop]
        est = None
        for k, v in DATASET_SIZE_THRESHOLDS.items():
            if k[0] < len(df) < k[1]:
                est = v

        #TODO: IterativeImputer works very slow for sparse for example qsar.arff dataset
        # if est is None:
        #     self._use_iterative_imputer = False
        # else:
        #     self._use_iterative_imputer = True
        #     self._imputer = IterativeImputer(estimator=est(), max_iter=self._imputer_rounds).fit(df[self._numeric_cols])

    def transform(self, df):
        super(NanPreprocessor, self).transform(df)

        df.drop(self._cols_to_drop, axis=1, inplace=True)

        if self._use_iterative_imputer:
            df[self._numeric_cols] = self._imputer.transform(df[self._numeric_cols])
        else:
            df[self._numeric_cols] = df[self._numeric_cols].fillna(0)

        return df
