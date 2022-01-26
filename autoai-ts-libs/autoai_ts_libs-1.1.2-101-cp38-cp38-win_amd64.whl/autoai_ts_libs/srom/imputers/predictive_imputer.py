from sklearn.utils.validation import check_array
from sklearn.impute import SimpleImputer
from sklearn.impute._base import _BaseImputer
from sklearn.base import clone
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from autoai_ts_libs.srom.imputers.base import TSImputer
from autoai_ts_libs.utils.messages.messages import Messages
import pandas as pd

class PredictiveImputer(_BaseImputer):
    """
    Predictive Imputer.
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill the backword and forward.
        order (int): lookback window.
        max_iter (int): number of iteration to conduct.
        tol (float): tolerance criteria for early stop.
        base_imputer(obj): base imputer object.
        model_imputer(obj): model imputer object.
    """

    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        max_iter=10,
        tol=1e-3,
        base_imputer=SimpleImputer(),
        base_model=RandomForestRegressor(n_estimators=10, n_jobs=-1, random_state=33),
    ):
        self.time_column = time_column
        self.missing_values = missing_values
        self.enable_fillna = enable_fillna
        self.order = order
        self.max_iter = max_iter
        self.tol = tol
        self.base_imputer = base_imputer
        self.base_model = base_model

    def fit(self, X, y=None, **fit_params):
        """    
        Fit the imputer
        Parameters:
            X(array like): input.
        """
        if 'skip_fit' in fit_params.keys() and fit_params['skip_fit']:
            return self

        X = check_array(X, dtype=np.float64, force_all_finite=False)

        if isinstance(X, pd.DataFrame):
            X = X.to_numpy()
        if not np.isnan(self.missing_values):
            X[X==self.missing_values] = np.NaN

        if isinstance(self.base_imputer, TSImputer):
            X_nan = np.isnan(self.base_imputer.get_X(X,order=self.order))
            self.most_by_nan = X_nan.sum(axis=0).argsort()[::-1]
            imputed = self.base_imputer.fit_transform(X)
            imputed = self.base_imputer.get_X(imputed, order=self.order)
        else:
            X_nan = np.isnan(X)
            self.most_by_nan = X_nan.sum(axis=0).argsort()[::-1]
            imputed = self.base_imputer.fit_transform(X)

        new_imputed = imputed.copy()
        gamma_ = []

        # one for each column (order)
        self.estimators_ = [clone(self.base_model) for _ in range(new_imputed.shape[1])]

        # run the model for max_iteration and train a model to predict missing value
        for _ in range(self.max_iter):
            # the order in which the nans are present
            for i in self.most_by_nan:
                # remove the column under consideration
                X_s = np.delete(new_imputed, i, 1)
                # the corresponding entry
                y_nan = X_nan[:, i]

                # remove rows where target is None
                X_train = X_s[~y_nan]
                y_train = new_imputed[~y_nan, i]
                # will be part of test and its entry will be predicted
                X_unk = X_s[y_nan]

                # train the corresponding estimators
                # all the estimators will be trained
                estimator_ = self.estimators_[i]
                estimator_.fit(X_train, y_train)

                if len(X_unk) > 0:
                    new_imputed[y_nan, i] = estimator_.predict(X_unk)

            # after one round, we will evaluate the difference
            gamma = (
                (new_imputed - imputed) ** 2 / (1e-6 + new_imputed.var(axis=0))
            ).sum() / (1e-6 + X_nan.sum())
            gamma_.append(gamma)
            if np.abs(np.diff(gamma_[-2:])) < self.tol:
                break

        return self

    def transform(self, X):
        """
        Transform the imputer
        Parameters:
            X(array like): input.
        """
        if X is None:
            return X
        X = check_array(X, dtype=np.float64, force_all_finite=False)

        if isinstance(X, pd.DataFrame):
            X = X.to_numpy()
        if not np.isnan(self.missing_values):
            X[X==self.missing_values] = np.NaN

        if isinstance(self.base_imputer, TSImputer):
            if len(X) < self.order:
                if np.count_nonzero(np.isnan(X)) > 0:
                    raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0057E'))
                else:
                    return X
            X_nan = np.isnan(self.base_imputer.get_X(X,order=self.order))
            X = self.base_imputer.fit_transform(X)
            X = self.base_imputer.get_X(X, order=self.order)
        else:
            X_nan = np.isnan(X)
            X = self.base_imputer.transform(X)

        # the order on imputation is different, this is little confusion
        for i, estimator_ in enumerate(self.estimators_):
            # again find the data
            X_s = np.delete(X, i, 1)
            y_nan = X_nan[:, i]
            X_unk = X_s[y_nan]
            if len(X_unk) > 0:
                X[y_nan, i] = estimator_.predict(X_unk)

        if isinstance(self.base_imputer, TSImputer):
            X = self.base_imputer.get_TS(X, order=self.order)

        return X