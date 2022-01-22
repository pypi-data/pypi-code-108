#from __future__ import annotations

import numpy as np
from sklearn.compose import ColumnTransformer


class PidsimColTransformer:   # TODO add docstring
  def __init__ (self, *args, **kwargs):

    if (len(args) == 1) and isinstance (args[0], ColumnTransformer):
      self._col_transformer = args[0]
    else:
      self._col_transformer = ColumnTransformer (*args, **kwargs)

  def fit (self, *args, **kwargs):
    self._col_transformer.fit (*args, **kwargs)

  def transform (self, *args, **kwargs):
    return self._col_transformer.transform (*args, **kwargs)

  def fit_transform (self, *args, **kwargs):
    return self._col_transformer.fit_transform (*args, **kwargs)

  def inverse_transform (self, X):
    X_tr = np.empty (shape = X.shape)   # initial array

    ## Transformers: ( (name, fitted_transformer, column) , ... )
    transformers = self._col_transformer.transformers_

    ## Numerical transformer
    num_transformer = transformers[0][1]
    num_cols = transformers[0][2]
    X_tr[:,num_cols] = num_transformer . inverse_transform (X[:,num_cols])

    ## Function transformer
    fnc_cols = transformers[1][2]
    X_tr[:,fnc_cols] = X[:,fnc_cols]

    return X_tr

  @property
  def sklearn_transformer (self) -> ColumnTransformer:
    return self._col_transformer
