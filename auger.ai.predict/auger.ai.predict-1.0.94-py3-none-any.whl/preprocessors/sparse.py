import pandas as pd
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
from sklearn.decomposition import PCA, IncrementalPCA

from auger_ml.preprocessors.base import BasePreprocessor


DATASET_SIZE_THRESHOLDS = {
    (1, 10**3): PCA,
    (10**3 + 1, 10**6): IncrementalPCA,
    (10**6 + 1, 10**10): None
}


class SparsePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(SparsePreprocessor, self).__init__(
            params=params,
            params_keys=['thresh_sparse', 'n_comp_frac']
        )
        self._thresh_sparse = params.get('thresh_sparse', 0.95)
        self._n_comp_frac = params.get('n_comp_frac', 0.2)

    def fit(self, df):
        super(SparsePreprocessor, self).fit(df)

        self._cols = []

        for c in df.select_dtypes(include=['float64', 'float32', 'float', 'float16']).columns:
            if df[c].value_counts().max() > len(df) * self._thresh_sparse:
                self._cols.append(c)

        n_comp = int(len(self._cols) * self._n_comp_frac)
        logging.info("SparsePreprocessor n_comp: %s" % n_comp)

        est = None
        for k, v in DATASET_SIZE_THRESHOLDS.items():
            if k[0] < len(df) < k[1]:
                est = v

        if est is None or n_comp < 2:
            self._pca = None
        else:
            self._pca = est(n_comp).fit(df[self._cols])

    def transform(self, df):
        super(SparsePreprocessor, self).transform(df)

        if self._pca is None:
            df = df.drop(self._cols, axis=1)
        else:
            df_pca = pd.DataFrame(self._pca.transform(df[self._cols]),
                                  columns=["pca_" + str(i) for i in range(self._pca.n_components)],
                                  index=df.index)

            df = pd.concat([df, df_pca], axis=1, copy=False)
            df.drop(self._cols, axis=1, inplace=True)

        return df
