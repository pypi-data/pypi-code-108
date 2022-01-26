# IBM Confidential Materials
# Licensed Materials - Property of IBM
# IBM Smarter Resources and Operation Management
# (C) Copyright IBM Corp. 2021 All Rights Reserved.
# US Government Users Restricted Rights
#  - Use, duplication or disclosure restricted by
#    GSA ADP Schedule Contract with IBM Corp.


"""
.. module:: Stack Regression
   :synopsis: Contains StackRegression class.

.. moduleauthor:: SROM Team
"""
import warnings
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.base import clone
import scipy.sparse as sparse

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class StackRegressor(BaseEstimator, RegressorMixin):
    """
    The stack regressor for scikit-learn estimators for regression. \

    Parameters:
        base_model (list of pipelines): This list contains a set of top-k performing pipeline.
        meta model (model) : this is also a model
        use_meta_features_only (boolean) : True or False
        refit (boolean) : True or False
        
    """

    def __init__(
        self, base_models, meta_model, use_meta_features_only=True, refit=True
    ):

        self.base_models = base_models
        self.meta_model = meta_model
        self.use_meta_features_only = use_meta_features_only
        self.refit = refit

    def fit(self, X, y):
        """
        fitting model
        """

        if self.refit:
            self.base_models_ = clone(self.base_models)
            self.meta_model_ = clone(self.meta_model)
        else:
            self.base_models_ = self.base_models
            self.meta_model_ = self.meta_model

        for regr in self.base_models_:
            regr.fit(X, y)

        _meta_features = self._generate_meta_features(X)

        if not self.use_meta_features_only:
            pass
        elif sparse.issparse(X):
            _meta_features = sparse.hstack((X, _meta_features))
        else:
            _meta_features = np.hstack((X, _meta_features))

        self.meta_model_.fit(_meta_features, y)

        return self

    def _generate_meta_features(self, X):
        return np.column_stack([bs_mdl.predict(X) for bs_mdl in self.base_models_])

    def predict(self, X):
        _meta_features = self._generate_meta_features(X)
        if not self.use_meta_features_only:
            pass
        elif sparse.issparse(X):
            _meta_features = sparse.hstack((X, _meta_features))
        else:
            _meta_features = np.hstack((X, _meta_features))
        return self.meta_model_.predict(_meta_features)
