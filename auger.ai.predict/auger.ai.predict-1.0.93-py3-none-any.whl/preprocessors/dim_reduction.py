from auger_ml.preprocessors.base import BasePreprocessor

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

import pandas as pd


SUPPORTED_ALGORITHMS = ["PCA", "t-SNE"]


class DimReductionPreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(DimReductionPreprocessor, self).__init__(
            params=params,
            params_keys=['alg_name', 'n_components']
        )

        self._transformer_name = params.get('alg_name', "t-SNE")
        self._n_components = params.get('n_components', 2)

        self._transformer = None

    def fit(self, df):
        super(DimReductionPreprocessor, self).fit(df)

        if self._transformer_name == "PCA":
            self._transformer = PCA(self._n_components)
            self._transformer.fit(df)
        elif self._transformer_name == "t-SNE":
            self._transformer = TSNE(self._n_components)
            #DO not call fit for TSNE since it do fit_transform
        else:
            raise ValueError(f"Unknown algorithm: {self._transformer_name}")


    def transform(self, df):
        super(DimReductionPreprocessor, self).transform(df)

        if self._transformer_name == "t-SNE":
            df = pd.DataFrame(self._transformer.fit_transform(df), columns=[f"comp_{i}" for i in range(self._n_components)])            
        else:    
            df = pd.DataFrame(self._transformer.transform(df), columns=[f"comp_{i}" for i in range(self._n_components)])

        return df
