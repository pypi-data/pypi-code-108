import pandas as pd
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import numpy as np

from auger_ml.preprocessors.base import BasePreprocessor


class CategoricalPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(CategoricalPreprocessor, self).__init__(
            params=params,
            params_keys=['cat_cols', 'max_categoricals_nunique', 'label_enc_cols']
        )

        self._BUCKET_CATEGORY = "BUCKET_CATEGORY"

        self._cat_cols = params.get('cat_cols', [])
        self._max_categoricals_nunique = params.get('max_categoricals_nunique', 50)
        self._label_enc_cols = params.get('label_enc_cols', [])

    def fit(self, df):
        super(CategoricalPreprocessor, self).fit(df)

        self._category_map = {}
        for k in self._cat_cols:
            if k in df.columns:
                self._category_map[k] = None

        # add implicit category columns
        for c in df.columns:
            if c.startswith("cat__"):
                self._category_map[c] = None
            elif not c in self._category_map and df.dtypes[c].name == 'object':
                raise ValueError("Feature %s is a string, change type to categorical or integer, or remove from features."%c)

        for c in self._category_map:
            if df.dtypes[c].name == 'object':
                vc = df[c].dropna().astype('unicode').value_counts()
            else:
                vc = df[c].dropna().value_counts()

            #vc = df[c].value_counts()
            if c in self._label_enc_cols:
                self._category_map[c] = {
                    "labels": vc.index.tolist(),
                    "major": [],
                    "minor": []
                }
            else:
                self._category_map[c] = {
                    "labels": [],
                    "major": vc.index[:self._max_categoricals_nunique].tolist(),
                    "minor": vc.index[self._max_categoricals_nunique:].tolist(),
                }

            # if len(self._category_map[c]['minor'])>0:
            #     self._category_map[c]['minor'].append(self._BUCKET_CATEGORY)

        #logging.info(self._category_map)

    def transform(self, df):
        super(CategoricalPreprocessor, self).transform(df)
        onehot_map = {}

        for c in self._category_map:
            if self._category_map[c]['labels']:
                df[c] = pd.Categorical(df[c], categories=self._category_map[c]['labels'])
                df[c] = df[c].cat.codes
            else:
                if self._category_map[c]['minor']:
                    df[c + "__labels"] = pd.Categorical(
                        df[c],
                        categories=self._category_map[c]['minor']
                    )#.fillna(self._BUCKET_CATEGORY)
                    df[c + "__labels"] = df[c + "__labels"].cat.codes

                if self._category_map[c]['major']:
                    df[c] = pd.Categorical(
                        df[c],
                        categories=self._category_map[c]['major']
                    )#.fillna(self._BUCKET_CATEGORY)
                    onehot_map[c] = self._category_map[c]

        # do encoding
        if onehot_map:
            df = pd.get_dummies(df, prefix_sep="__", columns=list(onehot_map.keys()), dummy_na=False, dtype=np.float32)

        #print(df.dtypes)

        return df
