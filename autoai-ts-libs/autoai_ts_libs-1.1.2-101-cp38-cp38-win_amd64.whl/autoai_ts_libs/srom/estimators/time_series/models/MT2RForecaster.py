import pandas as pd
import numpy as np
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from collections import namedtuple
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.base import BaseEstimator
from autoai_ts_libs.srom.estimators.time_series.models.base import SROMTimeSeriesForecaster
from autoai_ts_libs.srom.estimators.time_series.models.T2RForecaster import T2RForecaster
from sklearn.base import clone
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.utils.score import Score

class MT2RForecaster(BaseEstimator, SROMTimeSeriesForecaster):
    """
    Trend-to-Residual Multi-Step Multi-Variate Singal Predictor.
    Parameters
    ----------
        target_columns : (list of int) index of target cols .
        trend : (string, default = Linear) Trend model to be used. It can be Linear, Difference. 
        residual : (string, default = Linear) Residual model to be used. It can be Linear.     
        lookback_win : (int or string, default = auto) Look-back window for the model.
        prediction_win : (int, optional, default = 12) Look-ahead window for the model.
        n_jobs : (int, optional, default = -1) no of jobs.
    """

    def __init__(
        self,
        target_columns,
        trend="Linear",
        residual="Linear",
        lookback_win="auto",
        prediction_win=12,
        n_jobs=-1,
    ):
        self.trained_models = []
        self.trend = trend
        self.residual = residual
        if lookback_win == "auto" or isinstance(lookback_win,int):
            self.lookback_window = lookback_win
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0079E'))
        self.prediction_win = prediction_win
        self.base_model = T2RForecaster(
            trend=self.trend,
            residual=self.residual,
            lookback_win=self.lookback_window,
            prediction_win=self.prediction_win,
        )
        self.target_columns = target_columns

        if n_jobs == -1:
            n_jobs = cpu_count() -1
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = min(len(target_columns), n_jobs)

    @property
    def lookback_win(self):
        """
        """
        return self.lookback_window

    @property
    def lookback_window(self):
        """
        """
        if not hasattr(self,"lookback_window_"):
           self.lookback_window_ = 'auto'
           self.is_auto_lookback_win_ = True 

        if self.is_auto_lookback_win_:
            if len(self.trained_models) > 0 :
                lookback_win = []
                for model in self.trained_models:
                    lookback_win.append(model.i_lookback_win)
                return max(lookback_win)
            else:
                return self.lookback_window_
        elif isinstance(self.lookback_window_,int):
            return self.lookback_window_
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0079E'))

    @lookback_window.setter
    def lookback_window(self,lookback_win):
        """
        """
        if lookback_win == "auto":
            self.is_auto_lookback_win_ = True
        else:
            self.is_auto_lookback_win_ = False    
        self.lookback_window_ = lookback_win
            
    def name(self):
        return "MT2RForecaster"

    def _fit_single_model(self, X, idx, i):
        _x = X[:, i].reshape(-1, 1)
        model_i = self.trained_models[idx]
        model_i.fit(_x)
        return model_i

    def _parallel_fit(self, X, y=None):
        """
        Utility to parallelize the code.
        """
        self.trained_models = Parallel(n_jobs=self.n_jobs)(
            delayed(self._fit_single_model)(X, idx, item)
            for idx, item in enumerate(self.target_columns)
        )

    def _sequential_fit(self, X, y=None):
        """
        Utility to run code sequentially.
        """
        for idx, i in enumerate(self.target_columns):
            _x = X[:, i]
            _x = _x.reshape(-1, 1)
            self.trained_models[idx].fit(_x)

    def fit(self, X, y=None):
        """
        Fit the model.
        Parameters
        ----------
            X : (numpy array) input data.
        
        """
        
        # first time we create an empty model for each variable
        if len(self.trained_models) == 0:
            for idx, _ in enumerate(self.target_columns):
                self.trained_models.append(clone(self.base_model))

        if self.n_jobs > 1:
            self._parallel_fit(X)
        else:
            self._sequential_fit(X)
        return self

    def _sequential_predict(self, X=None):
        """
        This function is for predicting future.
        """
        for idx, i in enumerate(self.target_columns):
            # When X is none don't pass any input.
            if X is None:
                pred = self.trained_models[idx].predict()
            else:
                try:
                    pred = self.trained_models[idx].predict(X[:, i])
                except Exception as e:
                    raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0055E'))
            if len(self.trained_models) > 1:
                reshaped = pred.reshape(-1, 1)
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = pred
        return result.flatten().reshape(-1, len(self.trained_models))

    def _predict(self, X, idx, index):
        # When X is none don't pass any input.
        if X is None:
            pred = self.trained_models[idx].predict()
        else:
            pred = self.trained_models[idx].predict(X[:, index])

        return pred
    
    def _parallel_predict(self, X=None):
        """
        Utility to parallelize the code.
        """
        ret_preds = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict)(X, idx, item) for idx, item in enumerate(self.target_columns)
        )

        for i, row in enumerate(ret_preds):
            if len(self.trained_models) > 1:
                reshaped = row.reshape(-1, 1)
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = row
        return result.flatten().reshape(-1, len(self.trained_models))

    def predict(self, X=None, prediction_type=None):
        """
        This is to predict.
        Parameters
        ----------
            X : (numpy array) input data. It can be none as well.
            prediction_type : It can be sliding_window or forecast. Default is forecast.
        Returns
        -------
            numpy array.
        """
        if X is not None:
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        if prediction_type is not None:
            if prediction_type.lower() == Score.PREDICT_SLIDING_WINDOW:
                if self.prediction_win == 1:
                    return self.predict_sliding_window(X)
                elif self.prediction_win > 1:
                    return self.predict_multi_step_sliding_window(X,self.prediction_win)
                else:
                    raise Exception(Messages.get_message(prediction_type, message_id='AUTOAITSLIBS0046E'))
            elif prediction_type.lower() != Score.PREDICT_FORECAST:
                raise Exception(Messages.get_message(prediction_type, message_id='AUTOAITSLIBS0046E'))
        
        if isinstance(X, pd.DataFrame):
            X = np.array(X)
        if self.n_jobs > 1:
            return self._parallel_predict(X)
        else:
            return self._sequential_predict(X)

    def _predict_single_model(self, X, idx, i):
        return self.trained_models[idx].predict_sliding_window(
            X[:, i].reshape(-1, 1)
        )


    def _parallel_predict_sliding_window(self, X):
        """
        utility to parallelize the code.
        """
        self.ret_ans = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_single_model)(X, idx, item)
            for idx, item in enumerate(self.target_columns)
        )

        return pd.DataFrame(self.ret_ans).T.values

    def predict_sliding_window(self, X):
        """
        This method is for single step prediction.
        Parameters
        ----------
            X : (numpy array) input data.
        Returns
        -------
            numpy array.
        """
        y = self._parallel_predict_sliding_window(X)
        return y.reshape(-1, len(self.trained_models))

    def _predict_single_multi_step_model(self, X, idx, i, prediction_win):
        return self.trained_models[idx].predict_multi_step_sliding_window(
            X[:, i].reshape(-1, 1), prediction_win
        )

    def _parallel_predict_multi_step_sliding_window(self, X, prediction_win):
        """
        internal function for predict.
        """
        self.ret_ans = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_single_multi_step_model)(X, idx, item, prediction_win)
            for idx, item in enumerate(self.target_columns)
        )

        ret_ans = np.empty(
            [self.ret_ans[0].shape[0], prediction_win * len(self.trained_models)]
        )
        for dim_i in range(len(self.ret_ans)):
            for row_i in range(self.ret_ans[0].shape[0]):
                for col_i in range(prediction_win):
                    ret_ans[
                        row_i, col_i * len(self.trained_models) + dim_i
                    ] = self.ret_ans[dim_i][row_i, col_i]
        return ret_ans

    def predict_multi_step_sliding_window(self, X, prediction_win):
        """
        This method is for multi step prediction.
        Parameters
        ----------
            X : (numpy array) input data.
            prediction_win : (int, default=12) look ahead to be used for prediction.
        Returns
        -------
            numpy array.
        """
        y = self._parallel_predict_multi_step_sliding_window(X, prediction_win)
        return y.reshape(-1, len(self.trained_models))

    def predict_proba(self, X=None):
        """
        Prediction probability.
        Parameters
        ----------
            X : numpy array.
        Returns
        -------
            y : numpy array
        """
        if self.n_jobs > 1:
            return self._parallel_predict_proba(X)
        else:
            return self._sequential_predict_proba(X)

    def _sequential_predict_proba(self, X=None):
        """
        Helper function for predict_proba.
        """
        for idx, i in enumerate(self.target_columns):
            # When X is none don't pass any input.
            if X is None:
                pred = self.trained_models[idx].predict_interval()
            else:
                pred = self.trained_models[idx].predict_interval(X[:, i])
            # reshape by column and append by column.
            reshaped = pred.reshape(-1, 1, 2)
            if len(self.trained_models) > 1:
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = reshaped
        return result

    def _predict_proba(self, X, idx, index):
        # When X is none don't pass any input.
        if X is None:
            pred = self.trained_models[idx].predict_interval()
        else:
            pred = self.trained_models[idx].predict_interval(X[:, index])

        return pred

    def _parallel_predict_proba(self, X=None):
        """
        Helper function for predict_proba.
        """
        ret_preds = Parallel(n_jobs=self.n_jobs)(
            delayed(self._predict_proba)(X, idx, item) for idx, item in enumerate(self.target_columns)
        )

        for i, row in enumerate(ret_preds):
            reshaped = row.reshape(-1, 1, 2)
            if len(self.trained_models) > 1:
                if i == 0:
                    result = reshaped
                else:
                    result = np.hstack((result, reshaped))
            else:
                result = reshaped
        return result
