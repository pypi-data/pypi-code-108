import copy
import numpy as np
import multiprocessing

from sklearn.base import BaseEstimator

from catboost import CatBoostClassifier as CBClassifier
from catboost import CatBoostRegressor as CBRegressor


class CatBoostBase(BaseEstimator):
    def __init__(self, **params):
        self._params = params
        self._kitty = None
        self._estimator_type = 'classifier' if self.is_classifier else 'regressor'

    def fit(self, x, y, eval_set=None, verbose=False, early_stopping_rounds=None):
        params = copy.deepcopy(self._params)
        if 'n_jobs' in params:
            params['thread_count'] = params['n_jobs']
            if params['thread_count'] < 0:
                params['thread_count'] = multiprocessing.cpu_count()
                    
            del params['n_jobs']

        if self.is_classifier:
            self._kitty = CBClassifier(**params)
        else:    
            self._kitty = CBRegressor(**params)

        self._kitty.fit(X=x, y=y, eval_set=eval_set, early_stopping_rounds=early_stopping_rounds, verbose=verbose)
        return self

    def predict(self, x):
        return np.squeeze(self._kitty.predict(x))

    def predict_proba(self, x):
        return self._kitty.predict_proba(x)

    def get_params(self, deep=False):
        return self._params

    def score(self, x, y):
        return self._kitty.score(x, y)

    # def save_model(self, path):
    #     return self._kitty.save_model(path)

    # def load_model(self, path):
    #     from catboost import CatBoostClassifier, CatBoostRegressor

    #     if self.is_classifier:
    #         self._kitty = CatBoostClassifier()
    #     else:    
    #         self._kitty = CatBoostRegressor()

    #     return self._kitty.load_model(path)

    @property
    def feature_importances_(self):
        return self._kitty.feature_importances_

    @property
    def classes_(self):
        return self._kitty.classes_


class CatBoostClassifier(CatBoostBase):
    def __init__(self, n_jobs=1, **params):
        self.is_classifier = True
        super(CatBoostClassifier, self).__init__(**params)

    def get_params(self, deep=False):
        if not self._params:
            return {'n_jobs': 1,
                    'loss_function': 'Logloss',
                    'allow_writing_files': False,
                    'learning_rate': 0.03,
                    'n_estimators': 800,
                    'depth': 6,
                    'border_count': 128,
                    'rsm': 1.0,
                    'l2_leaf_reg': 3.0,
                    'model_size_reg': 0.5,
                    'feature_border_type': 'GreedyLogSum'}
        else:
            return self._params


class CatBoostRegressor(CatBoostBase):
    def __init__(self, n_jobs=1, **params):
        self.is_classifier = False
        super(CatBoostRegressor, self).__init__(**params)

    def get_params(self, deep=False):
        if self._params:
            return {'n_jobs': 1,
                    'loss_function': 'RMSE',
                    'allow_writing_files': False,
                    'learning_rate': 0.03,
                    'n_estimators': 800,
                    'depth': 6,
                    'border_count': 128,
                    'rsm': 1.0,
                    'l2_leaf_reg': 3.0,
                    'model_size_reg': 0.5,
                    'feature_border_type': 'GreedyLogSum'}
        else:
            return self._params

