import numpy as np 
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances
from autoai_ts_libs.utils.messages.messages import Messages

class DataTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """

    def __init__(self):
        pass

    def fit(self, X, y=None):
        X = check_array(X, accept_sparse=True)
        self.n_features_ = X.shape[1]
        return self

    def transform(self, X):
        check_is_fitted(self, 'n_features_')
        X = check_array(X, accept_sparse=True)

        if X.shape[1] != self.n_features_:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0026E'))
        pass

class StateFulTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """

class TargetTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """

    def inverse_transform(self, y):
        pass
