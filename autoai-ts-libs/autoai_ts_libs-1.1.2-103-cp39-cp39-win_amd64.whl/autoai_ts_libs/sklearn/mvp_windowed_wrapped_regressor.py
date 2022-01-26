from sklearn.multioutput import MultiOutputRegressor
from sklearn.base import BaseEstimator

# MOR does not handle single variable, we need this wrapped estimator to handle both single
# variable case and multi-variable case


class AutoaiWindowedWrappedRegressor(BaseEstimator):
    def __init__(self, regressor=None, n_jobs=None):
        self.regressor = regressor
        self.n_jobs = n_jobs

    def __repr__(self):
        return f'{self.__class__.__name__}({self.regressor.__class__.__name__})'

    def fit(self, X, y):
        self.regressor_ = self.regressor
        if y.ndim > 1:  # check if y has more than 1 dimension
            if y.shape[1] > 1:  # check to avoid y has shape of (N, 1), 2 dimensions but still is a vector
                self.regressor_ = MultiOutputRegressor(estimator=self.regressor, n_jobs=self.n_jobs)

        self.regressor_.fit(X,y)
        return self

    # attempt to have a uniform interface for returning the internal estimator from our metaestimators
    @property
    def get_estimators(self):
        if hasattr(self, 'regressor_') and hasattr(self.regressor_, 'estimators_'):
            return self.regressor_.estimators_
        else:
            return [getattr(self, 'regressor_', getattr(self, 'regressor', None))]

    def predict(self, X):
        return self.regressor_.predict(X)
