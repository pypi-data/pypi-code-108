import pandas as pd
import numpy as np
import math
import scipy.stats as st
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from collections import namedtuple
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.base import BaseEstimator
from autoai_ts_libs.srom.estimators.time_series.models.base import SROMTimeSeriesForecaster
from autoai_ts_libs.utils.messages.messages import Messages


class MeanEstimator(BaseEstimator):
    """
    This class is to preserve the mean of signal.
    """

    def fit(self, x, y=None):
        """
        This is to fit.
        """
        self.z = np.mean(x)
        return self

    def predict(self, x):
        """
        This is to predict.
        """
        return np.zeros(len(x)) + self.z


class PolyEstimator(BaseEstimator):
    """
    Poly line estimators.
    Parameters
    ----------
        degree : (int, default = 2) Degree of polynomial. 
    """

    def __init__(self, degree=2):
        self.degree = degree

    def fit(self, x, y):
        """
         This is to fit.
        """
        self.base_model = np.poly1d(np.polyfit(x.flatten().tolist(), y, self.degree))
        return self

    def predict(self, x):
        """
        This is to predict.
        """
        return self.base_model(x.flatten().tolist())


class TrendEstimator(BaseEstimator):
    """
    Trend line Estimator.
    Parameters
    ----------
        base_model : (object, default = LinearRegression) Instance of base model to be used. 
    """

    def __init__(self, base_model=LinearRegression()):
        self.base_model = base_model

    def fit(self, x, y):
        """
        This is to fit.
        """
        self.base_model.fit(x, y)
        return self

    def predict(self, x):
        """
        This is to predit.
        """
        return self.base_model.predict(x)


class FourierTermEstimator(BaseEstimator):
    """
    FourierTermEstimator Estimator.
    Parameters
    ----------
        base_model : (object, default = LinearRegression) Instance of base model to be used.
    """

    def __init__(self, period, terms=3):
        self.period = period
        self.terms = terms

    def _get_feature_names(self):
        return [
            "Four_%s%s-%s" % ("S" if i % 2 == 0 else "C", str(self.period), str(i // 2))
            for i in range(self.total_dims_)
        ]

    def fit(self, x=None, y=None):
        """
        This is to fit.
        """
        if self.terms > self.period:
            self.terms = self.period
        self.p_ = ((np.arange(self.terms) + 1) / self.period).astype(np.float64)
        self.total_dims_ = len(self.p_) * 2
        print(self.total_dims_)
        self.feature_names_ = self._get_feature_names()
        return self

    def predict(self, x):
        """
        This is to predit.
        """
        _pred = []
        for e in self.p_:
            _pred.append(np.sin(np.pi * 2 * e * x))
            _pred.append(np.cos(np.pi * 2 * e * x))
        return np.asarray(_pred).T


class GeneralizedDifferenceRegressor(BaseEstimator):
    """
    GeneralizedDifferenceRegressor.
    Parameters
    ----------
        model : (object, default = LinearRegression) Instance of base model to be used.
    """

    def __init__(self, model=LinearRegression()):
        self.model = model

    def fit(self, x, y):
        """
        This is to fit.
        """
        y = y - x[:, 0]
        for item in range(1, x.shape[1]):
            x[:, item - 1] = x[:, item - 1] - x[:, item]
        self.model.fit(x[:, range(x.shape[1] - 1)], y)
        return self

    def predict(self, x):
        """
        This is to predict.
        """
        x1 = x.copy()
        for item in range(1, x1.shape[1]):
            x1[:, item - 1] = x1[:, item - 1] - x1[:, item]
        return self.model.predict(x1[:, range(x1.shape[1] - 1)]) + x[:, 0]


class GeneralizedMeanRegressor(BaseEstimator):
    """
    GeneralizedMeanRegressor.
    Parameters
    ----------
        model : (object, default = LinearRegression) Instance of base model to be used. 
    """

    def __init__(self, model=LinearRegression()):
        self.model = model

    def fit(self, x, y):
        """
        This is to fit.
        """
        x = np.hstack((x, np.mean(x, axis=1).reshape(-1, 1)))
        self.model.fit(x, y)
        return self

    def predict(self, x):
        """
        This is to predict.
        """
        x = np.hstack((x, np.mean(x, axis=1).reshape(-1, 1)))
        return self.model.predict(x)


class T2RForecaster(BaseEstimator, SROMTimeSeriesForecaster):
    """
    Trend-to-Residual Multi-Step Singal Predictor.
        
    Parameters
    ----------
        trend : (string, default = Linear) It can be Linear, Mean, Poly.
        residual : (string, default = Linear) It can be Linear, Difference. 
        lookback_win : (int or string, default = auto) Look-back window for the model.
        prediction_win : (int, optional, default = 12) Look-ahead window for the model.
    """

    def __init__(
        self, trend="Linear", residual="Linear", lookback_win="auto", prediction_win=12
    ):

        self.trend = trend
        self.residual = residual
        self.lookback_win = lookback_win
        self.prediction_win = prediction_win
        
        if self.lookback_win == "auto":
            self.i_lookback_win = "auto"
        else:
            self.i_lookback_win = self.lookback_win

        # initialize the trend model
        if self.trend == "Linear":
            self.trend_model = TrendEstimator(base_model=LinearRegression())
        elif self.trend == "Poly":
            self.trend_model = PolyEstimator(degree=2)
        elif self.trend == "Mean":
            self.trend_model = MeanEstimator()
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0038E'))

        # initialize the residual model
        if self.residual == "Linear":
            self.residual_model = LinearRegression()
        elif self.residual == "Difference":
            self.residual_model = GeneralizedDifferenceRegressor()
        elif self.residual == "GeneralizedMean":
            self.residual_model = GeneralizedMeanRegressor()
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0039E'))

    def _add_artifical_time_column(self):
        """
        This is utility function to store intermediate data.
        It add two new columns: row_number and artificial time
        also it store the min time, max time and deltaT.
        """
        self.X["row_number"] = np.arange(0, self.X.shape[0])
        self.X["time"] = self.X["row_number"]
        self.maxT = self.X["time"].max()
        self.minT = self.X["time"].min()
        self.deltaT = 1

    def fit(self, X, y=None):
        """
        Fit the model.
        Parameters
        ----------
            X : (numpy array) input data.
            y : None.
        Returns
        -------
            self : object
        """
        # automatically infer the lookback window for this model (only one time)
        if self.i_lookback_win == "auto":
            from autoai_ts_libs.srom.estimators.time_series.models.period_detection import (
                guess_period,
            )

            self.i_lookback_win = guess_period(X.flatten())
            if self.i_lookback_win == 0:
                self.i_lookback_win = 5
        # this model store X for further processing
        # we use column signal
        self.X = pd.DataFrame(X, columns=["Singal"])
        self.data_shape = self.X.shape
        self._add_artifical_time_column()

        # fit a trend model that predict time --> singal value
        self.trend_model.fit(self.X["time"].values.reshape(-1, 1), self.X["Singal"])

        # use trained model to fill Trend and Trend_Res
        self.X["Trend"] = self.trend_model.predict(self.X["time"].values.reshape(-1, 1))
        self.X["Trend_Res"] = self.X["Singal"] - self.X["Trend"]

        # trend model residual stdev to be used in predict interval
        trend_res = self.X["Trend_Res"].values
        sum_errs = np.sum((trend_res) ** 2)
        self.trend_res_stdev = np.sqrt(1 / (len(trend_res) - 2) * sum_errs)

        # prepare data to build second residual model using lookback window information
        self.X_col = ["Trend_Res"]
        for lag_i in range(1, self.i_lookback_win):
            self.X_col.append("Trend_Res_" + str(lag_i))
            self.X["Trend_Res_" + str(lag_i)] = self.X["Trend_Res"].shift(lag_i)
        # since this are recursive model, they take next
        self.X["Trend_Res_y"] = self.X["Trend_Res"].shift(-1)

        # training residual model
        tmpData = self.X[self.X_col + ["Trend_Res_y"]].dropna().copy()
        close_to_zero = 0.0000000001
        if np.sum(tmpData.sum()) == 0.0:
            tmpData = tmpData.replace(0.0, close_to_zero)
        near_zero = np.sum(np.sum(np.abs(tmpData) < close_to_zero))
        if near_zero == tmpData.shape[0] * tmpData.shape[1]:
            tmpData[np.abs(tmpData) < close_to_zero] = close_to_zero
        self.residual_model.fit(tmpData[self.X_col].values, tmpData["Trend_Res_y"])

        # residual model residual stdev to be used in predict interval
        ypred = self.residual_model.predict(tmpData[self.X_col].values)
        ytrue = tmpData["Trend_Res_y"].values
        sum_errs = np.sum((ytrue - ypred) ** 2)

        self.res_res_stdev = np.sqrt(1 / (len(ytrue) - 2) * sum_errs)
        # trim the X, there are additional information that is not
        # used, so we trim it them
        # the following line failed so do not try
        self.predict_lookup = list(self.X.loc[self.X.index[-1], :][self.X_col])
        self.X = self.X[["Singal"]].copy()

        return self

    def update_multiple_observations(self, newX, pred_horizon=1):
        """
        This is a utility for speedup.
        It append multiple observations together and increase the speedup.
        """

        # temporary merge data of train and incoming
        _X = self.X["Singal"]
        _X = pd.DataFrame(_X, columns=["Singal"])
        _nX = pd.DataFrame(newX, columns=["Singal"])
        _X = _X.append(_nX)
        _X.reset_index(inplace=True, drop=True)

        # add row number and time column
        _X["row_number"] = np.arange(0, _X.shape[0])
        _X["time"] = _X["row_number"]

        # add trend and residual value
        _X["Trend"] = self.trend_model.predict(_X["time"].values.reshape(-1, 1))
        _X["Trend_Res"] = _X["Singal"] - _X["Trend"]

        # prepare lookback window dataset
        for lag_i in range(1, self.i_lookback_win):
            _X["Trend_Res_" + str(lag_i)] = _X["Trend_Res"].shift(lag_i)

        # now we start predicting the model
        tmpData = _X.dropna().copy()
        tmpData["pred_residual"] = self.residual_model.predict(
            tmpData[self.X_col].values
        )
        # this is very imp as we predict for next step, so we gave the value
        tmpData["pred_residual_1"] = tmpData["pred_residual"].shift(1)
        tmpData["predicted_y"] = tmpData["pred_residual_1"] + tmpData["Trend"]
        tmpData["predicted_y_0"] = tmpData["predicted_y"]
        tmpData = tmpData.dropna()

        # if we wanted to do recursive multi-step using recursive meachnisum
        # note that we add additional prediction in same row
        impClm = ["predicted_y_0"]
        for i in range(1, pred_horizon):

            # our current prediction become signal
            tmpData["Singal"] = tmpData["predicted_y"]
            # we want to predict next time
            tmpData["time"] = tmpData["time"] + 1

            # calculate the real trend_res
            tmpData["Trend_Res"] = tmpData["Singal"] - tmpData["Trend"]

            # make prediction
            tmpData["pred_residual"] = self.residual_model.predict(
                tmpData[self.X_col].values
            )
            tmpData["Trend"] = self.trend_model.predict(
                tmpData["time"].values.reshape(-1, 1)
            )
            tmpData["predicted_y_" + str(i)] = (
                tmpData["pred_residual"] + tmpData["Trend"]
            )
            tmpData["predicted_y"] = tmpData["predicted_y_" + str(i)]
            impClm.append("predicted_y_" + str(i))

            # predict trend based on time
            # reassign the row value to old
            for lag_i in reversed(range(2, self.i_lookback_win)):
                tmpData["Trend_Res_" + str(lag_i)] = tmpData[
                    "Trend_Res_" + str(lag_i - 1)
                ]
            # fill the first one
            tmpData["Trend_Res_1"] = tmpData["Trend_Res"]

        if pred_horizon == 1:
            return tmpData["predicted_y_0"].values[-1 * newX.shape[0] :]
        else:
            return tmpData[impClm].values[-1 * newX.shape[0] : -pred_horizon + 1, :]

    def update_single_observation(self, newX):
        """
        This utility is to update single observations in the system.
        This is very slow process. So we request to use multiple
        """
        # start from creating new dataframe
        newX = pd.DataFrame(newX, columns=["Singal"])

        # make necessary checks to be passed
        if newX.shape[1] != self.data_shape[1]:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0040E'))
        # only one record is supported
        if newX.shape[0] != 1:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0041E'))

        # adding row_number and time
        newX["row_number"] = self.X.shape[0]
        newX["time"] = newX["row_number"]

        # use time to predict (expected) trend, and Trend_Res
        newX["Trend"] = self.trend_model.predict(newX["time"].values.reshape(-1, 1))
        newX["Trend_Res"] = newX["Singal"] - newX["Trend"]

        # update X also, one of the Trend_Res_y
        self.X.loc[self.X.index[-1], "Trend_Res_y"] = newX["Trend_Res"].values[0]

        # create a feature vection for feature usage
        newX["Trend_Res_1"] = self.X.loc[self.X.index[-1], "Trend_Res"]
        for lag_i in range(2, self.i_lookback_win):
            newX["Trend_Res_" + str(lag_i)] = self.X.loc[
                self.X.index[-1], "Trend_Res_" + str(lag_i - 1)
            ]
        newX["Trend_Res_y"] = np.NaN

        # merge newX into X
        self.X = self.X.append(newX)
        self.X.reset_index(inplace=True, drop=True)
        self.maxT = self.X["time"].max()

    def _prepare_predict_X(self, newX):
        """
        This is the internal method for predict.
        """
        _X = self.X["Singal"]
        _X = pd.DataFrame(_X, columns=["Singal"])
        _nX = pd.DataFrame(newX, columns=["Singal"])
        _X = _X.append(_nX)
        _X.reset_index(inplace=True, drop=True)

        # add row number and time column
        _X["row_number"] = np.arange(0, _X.shape[0])
        _X["time"] = _X["row_number"]

        # add trend and residual value
        _X["Trend"] = self.trend_model.predict(_X["time"].values.reshape(-1, 1))
        _X["Trend_Res"] = _X["Singal"] - _X["Trend"]
        res_array = list(_X["Trend_Res"])[-1 * self.i_lookback_win :]
        res_array.reverse()
        return _X["time"].max(), res_array

    def predict(self, X=None, prediction_win=None):
        """
        This method  is used for predicting future.
        Parameters
        ----------
            X : None.
            prediction_win : (int, default=12) look ahead to be used for prediction.
        Returns
        -------
            numpy array.
        """
        if prediction_win is None:
            prediction_win = self.prediction_win

        if X is None:
            # my first starting point is the last record we have in system
            start_v = self.predict_lookup.copy()
            pred = []
            for next_p in range(prediction_win):
                # residual model to predict the future residual
                ans = self.residual_model.predict(np.array(start_v).reshape(1, -1))
                # output of trend model to predict the trend
                ans_1 = self.trend_model.predict(
                    np.array(self.maxT + next_p + 1).reshape(1, -1)
                )

                # adjustment if array is produced
                if isinstance(ans_1, list):
                    ans_1 = ans_1[0]
                # prediction
                real_p = list(ans + ans_1)[0]
                pred.append(real_p)

                # since it is recursive, we put current residual at the first and pop the last one
                start_v.pop()
                start_v.insert(0, ans[0])

                # start_v is used in next iteration

            # return the final result
            return np.array(pred)
        else:
            # this method is an experimental.
            # prepare X first
            maxT, start_v = self._prepare_predict_X(X)
            pred = []
            for next_p in range(prediction_win):
                # residual model to predict the future residual
                ans = self.residual_model.predict(np.array(start_v).reshape(1, -1))
                # output of trend model to predict the trend
                ans_1 = self.trend_model.predict(
                    np.array(maxT + next_p + 1).reshape(1, -1)
                )

                # adjustment if array is produced
                if isinstance(ans_1, list):
                    ans_1 = ans_1[0]
                # prediction
                real_p = list(ans + ans_1)[0]
                pred.append(real_p)

                # since it is recursive, we put current residual at the first and pop the last one
                start_v.pop()
                start_v.insert(0, ans[0])

                # start_v is used in next iteration

            # return the final result
            return np.array(pred)

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
        return self.update_multiple_observations(X, pred_horizon=1)

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
        return self.update_multiple_observations(X, pred_horizon=prediction_win)

    def predict_interval(self, X=None, prediction_win=None, percentile=95):
        """
        This method  is used for getting predict_interval.
        Parameters
        ----------
            X : None.
            prediction_win : (int, default=12) look ahead to be used for prediction.
            percentile : (int default=95)
        Returns
        -------
            numpy array.
        """

        if prediction_win is None:
            prediction_win = self.prediction_win

        zval = st.norm.ppf(1 - ((100 - percentile) * 0.01 / 2))
        
        pred = []

        pred_itervals = []
        ans_interval = zval * self.res_res_stdev
        ans_1_interval = zval * self.trend_res_stdev

        if X is None:
            start_v = self.predict_lookup.copy()
            for next_p in range(prediction_win):
                # residual model to predict the future residual
                ans = self.residual_model.predict(np.array(start_v).reshape(1, -1))
                # lower and upper values for ans
                lower_ans, upper_ans = ans - ans_interval, ans + ans_interval
                # output of trend model to predict the trend
                ans_1 = self.trend_model.predict(
                    np.array(self.maxT + next_p + 1).reshape(1, -1)
                )
                # adjustment if array is produced
                if isinstance(ans_1, list):
                    ans_1 = ans_1[0]
                # lower and upper values for ans1
                lower_ans_1, upper_ans_1 = (
                    ans_1 - ans_1_interval,
                    ans_1 + ans_1_interval,
                )

                # prediction
                real_p = list(ans + ans_1)[0]
                pred.append(real_p)

                # pred interval
                lower_real_p = list(lower_ans + lower_ans_1)[0]
                upper_real_p = list(upper_ans + upper_ans_1)[0]
                pred_itervals.append([lower_real_p, upper_real_p])

                # since it is recursive, we put current residual at the first and pop the last one
                start_v.pop()
                start_v.insert(0, ans)
                # start_v is used in next iteration
        else:
            # this method is an experimental.
            # prepare X first
            maxT, start_v = self._prepare_predict_X(X)
            pred = []
            for next_p in range(prediction_win):
                # residual model to predict the future residual
                ans = self.residual_model.predict(np.array(start_v).reshape(1, -1))
                # lower and upper values for ans
                lower_ans, upper_ans = ans - ans_interval, ans + ans_interval
                # output of trend model to predict the trend
                ans_1 = self.trend_model.predict(
                    np.array(maxT + next_p + 1).reshape(1, -1)
                )

                # adjustment if array is produced
                if isinstance(ans_1, list):
                    ans_1 = ans_1[0]

                # prediction
                real_p = list(ans + ans_1)[0]
                pred.append(real_p)

                # pred interval
                lower_ans_1, upper_ans_1 = (
                    ans_1 - ans_1_interval,
                    ans_1 + ans_1_interval,
                )
                lower_real_p = list(lower_ans + lower_ans_1)[0]
                upper_real_p = list(upper_ans + upper_ans_1)[0]
                pred_itervals.append([lower_real_p, upper_real_p])

                # since it is recursive, we put current residual at the first and pop the last one
                start_v.pop()
                start_v.insert(0, ans[0])

        # return the final result
        return np.array(pred_itervals)
