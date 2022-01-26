from autoai_ts_libs.sklearn.small_data_window_transformers import (
    SmallDataWindowTargetTransformer,
)
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import (
    WindowTransformerMTS,
)
from autoai_ts_libs.sklearn.small_data_standard_row_mean_center_transformers import (
    StandardRowMeanCenterMTS,
)
from autoai_ts_libs.utils.messages.messages import Messages
from sklearn.compose import TransformedTargetRegressor
from sklearn.impute import SimpleImputer
import numpy as np
from autoai_ts_libs.utils.messages.messages import Messages


class AutoaiWindowTransformedTargetRegressor(TransformedTargetRegressor):
    def __init__(
        self,
        feature_columns=None,
        target_columns=None,
        regressor=None,
        lookback_window=10,
        prediction_horizon=1,
        scaling_func=None,
        inverse_scaling_func=None,
        check_inverse=False,
        short_name="",
        one_shot=False,
        row_mean_center=False,
        estimator_prediction_type="forecast",
        time_column=-1,
        random_state=42,
    ):

        self.prediction_horizon = prediction_horizon
        self.lookback_window = lookback_window
        # self.one_shot = one_shot
        self.row_mean_center = row_mean_center
        self.estimator_prediction_type = estimator_prediction_type
        self.cached_last_window_train_set_ = None

        # A pipeline could not be cloned because this init changed these input parameters. For now, we do not need them.
        # if func is None:
        #     self.func = self.function
        # else:
        #     self.func = func
        # if inverse_func is None:
        #     self.inverse_func = self.inverse_function
        # else:
        #     self.inverse_func = inverse_func

        # self.scaling_func = scaling_func
        # self.inverse_scaling_func = inverse_scaling_func
        # self.target_transformer = None
        self.short_name = short_name
        # self.ymean = None  # used in inverse_function to fill in inf/-inf and nan value
        self.forecasts_ = None  # used to keep forecasts of trainset

        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.time_column = time_column

        self.random_state = random_state

        super().__init__(
            regressor=regressor,
            transformer=None,
            func=self.function,
            inverse_func=self.inverse_function,
            check_inverse=check_inverse,
        )
        self._check_args()

    def _check_args(self):
        if self.time_column != -1:
            raise Exception(Messages.get_message(message_id="AUTOAITSLIBS0058E"))
        
        # if either feature or target columns are present, they need to be equal
        if (self.feature_columns or self.target_columns) and (self.feature_columns != self.target_columns):
            raise ValueError("Target columns must equal feature columns")


    def __repr__(self):
        return f"{self.regressor}"

    def function(self, y):
        if not self.row_mean_center:
            y = SmallDataWindowTargetTransformer(prediction_horizon=1).transform(X=y)
            y = SimpleImputer().fit_transform(y)

        return y

        # if self.one_shot:
        #     y = SmallDataWindowTargetTransformer(prediction_horizon=self.prediction_horizon).transform(X=y)
        # else:
        #     y = SmallDataWindowTargetTransformer(prediction_horizon=1).transform(X=y)
        #
        # y = SimpleImputer().fit_transform(y)
        #
        # # if self.scaling_func:  # transform the target y
        # #     power_transformer = PowerTransformer()
        # #     y2 = y
        # #     if y.ndim == 1:
        # #         y2 = y.reshape(y.shape[0], -1)
        # #     self.power_transformer = power_transformer.fit(X=y2)
        # #     transformed_y = self.power_transformer.transform(X=y2)
        # #     if y.ndim == 1:
        # #         y = transformed_y.flatten()
        # #     else:
        # #         y = transformed_y
        #
        # if self.scaling_func is None:
        #     return y
        #
        # y2 = y
        # self.ymean = np.mean(y2, axis=0)  # keep a vector of means, row-wise, or each column has one mean
        #
        # if y.ndim == 1:
        #     y2 = y.reshape(y.shape[0], 1)
        #
        # # first use PowerTransformer
        # self.target_transformer = PowerTransformer()
        # self.target_transformer.fit(X=y2)  # fit the transformer
        # transformed_y = self.target_transformer.transform(X=y2)
        #
        # if (np.count_nonzero(transformed_y) == 0) or (np.any(np.isinf(transformed_y))):
        #     # if all elements are 0 OR at least one element is inf or -inf
        #     self.target_transformer = StandardScaler()
        #     self.target_transformer.fit(X=y2)  # fit the transformer
        #
        #     transformed_y = self.target_transformer.transform(X=y2)
        #     if y.ndim == 1:
        #         y = transformed_y.flatten()
        #     else:
        #         y = transformed_y
        #
        #     return y
        # else:
        #     # if exists at least one none-zero elements OR none of inf or -inf elements
        #     if y.ndim == 1:
        #         y = transformed_y.flatten()
        #     else:
        #         y = transformed_y
        #
        #     return y

    def inverse_function(self, y):
        # Attention: this is not a precise inverse of the Windowing transformer
        # if self.inverse_scaling_func:
        #     y = self.inverse_scaling_func(y)

        return y

        # if self.inverse_scaling_func is None or self.target_transformer is None:
        #     return y
        #
        # y2 = y
        # if y.ndim == 1:
        #     y2 = y.reshape(y.shape[0], 1)
        #
        # inverse_y = self.target_transformer.inverse_transform(X=y2)
        # # check for inf and nan values
        # if (np.any(np.isinf(inverse_y)) or np.any(np.isnan(inverse_y))) and self.ymean is not None:
        #     df = pd.DataFrame(inverse_y)  # use DataFrame utility
        #     for idx, col in enumerate(df.columns):
        #         df[col].replace(inf, self.ymean[idx], inplace=True)
        #         df[col].replace(-inf, self.ymean[idx], inplace=True)
        #         df[col].replace(np.nan, self.ymean[idx], inplace=True)
        #
        #     inverse_y = df.values
        #
        # if y.ndim == 1:
        #     y = inverse_y.flatten()
        # else:
        #     y = inverse_y
        #
        # return y

    def _input_data_transformation(self, X):
        """
        Used to extract the proper columns of X, corresponding to features.
        
        Args:
            X : numpy array.
        """
        if hasattr(self, "feature_columns") and self.feature_columns:
            return X[:, self.feature_columns]
        return X

    def _output_data_transformation(self, X):
        """
        Used to extract the proper columns of X to create y, the target columns.
        
        Args:
            X : numpy array.
        """
        if hasattr(self, "target_columns") and self.target_columns:
            return X[:, self.target_columns]
        return X
        
    def _check_features_targets(self, X):
        """Check to make sure features and targets are meaningful. If they are 
        none, all columns will be used for both (original behavior)
        Args:
            X (numpy.ndarray]): Input data
        Raises:
            ValueError: Either both feature and target columns should be none 
                (original behavior) or they should both be specified.
        """
        if (self.feature_columns and not self.target_columns) or (not self.feature_columns and self.target_columns):
            raise ValueError("If one of feature or target columns is specified, they must both be specified.")
        
        if not self.feature_columns and not self.target_columns:
            self.feature_columns = [i for i in range(X.shape[1]) if i != self.time_column]
            self.target_columns = self.feature_columns

    def fit(self, X, y):
        # X2 = X
        # if self.row_mean_center:
        #     window_transformer = WindowTransformerMTS(lookback_window=self.lookback_window)
        #     rowmean_transformer = StandardRowMeanCenterMTS(lookback_window=self.lookback_window)
        #     (Xw, yw) = window_transformer.fit_transform(X, y)
        #     (X, y) = rowmean_transformer.fit_transform(Xw, yw)
        #
        # super().fit(X, y)  # set internal states
        #
        # # create forecasts immediately beyond training set
        # if X2.shape[0] > 2 * self.lookback_window:
        #     self.forecasts_ = self.predict_rowwise_2d(X=X2[-2 * self.lookback_window:, ])
        # else:
        #     self.forecasts_ = self.predict_rowwise_2d(X=X2)
        #
        # self.forecasts_ = self.forecasts_[-1:, ]  # keep only predictions of the last row
        # return self

        # clm_index = list(set(self.feature_columns + self.target_columns))

        # num_time_series = X.shape[1]  # number of time series

        self._check_features_targets(X)
        random_state = getattr(self, "random_state", None)
        num_time_series = len(self.target_columns)

        # keep last window in train set
        if X.shape[0] > self.lookback_window:
            self.cached_last_window_train_set_ = X[
                -self.lookback_window :,
            ]
        else:
            self.cached_last_window_train_set_ = X

        # get the right X y
        y = self._output_data_transformation(X)
        X = self._input_data_transformation(X)

        if self.row_mean_center:
            window_transformer = WindowTransformerMTS(
                lookback_window=self.lookback_window
            )
            rowmean_transformer = StandardRowMeanCenterMTS(
                lookback_window=self.lookback_window,
                random_state=random_state
            )
            (Xw, yw) = window_transformer.fit_transform(X, y)
            (X, y) = rowmean_transformer.fit_transform(Xw, yw)

        super().fit(X, y)  # set internal states

        # create forecasts immediately beyond training set
        X_cached = self.cached_last_window_train_set_
        # X_cached = self._input_data_transformation(X_cached)

        self.forecasts_ = self.predict_rowwise_2d(X=X_cached)
        self.forecasts_ = self.forecasts_[
            -1:,
        ]  # keep only predictions of the last row
        self.forecasts_ = self.forecasts_.reshape(
            -1, num_time_series
        )  # reshape to h x k, where k is number of time series, h is prediction horizon

        return self

    # prediction_type: forecast, rowwise, rowwise_2d
    def predict(self, X=None, prediction_type=None):
        if X is not None:
            if np.count_nonzero(np.isnan(X)) > 0:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0067E'))

        if prediction_type is None:
            prediction_type = self.estimator_prediction_type

        expected_method_name = f"predict_{prediction_type}"
        method = getattr(self, expected_method_name, None)
        if not method:
            raise ValueError(
                Messages.get_message({prediction_type}, message_id="AUTOAITSLIBS0011E")
            )

        return method(X=X)

    def predict_forecast(self, X=None):
        if X is None:
            return self.forecasts_
        try:
            num_time_series = len(self.target_columns) if hasattr(self, "target_columns") else X.shape[1]
            # prepend the last window of train set
            Xnew = np.concatenate((self.cached_last_window_train_set_, X), axis=0)
        except Exception as e:
            raise Exception(
                Messages.get_message(str(e), message_id="AUTOAITSLIBS0055E")
            )
        # take only the last window
        Xnew = Xnew[
            -self.lookback_window :,
        ]
        # Xnew = self._input_data_transformation(Xnew)

        # call row prediction
        y_pred = self.predict_rowwise_2d(X=Xnew)
        # take the last row of y_pred
        y_pred = y_pred[
            -1:,
        ]
        # return correct shape of h x k
        return y_pred.reshape(
            -1, num_time_series
        )  # reshape to h x k, where k is number of time series, h is prediction horizon

    # This method is responsible for:
    # 1. prepend last window of train set to input X
    # 2. call predict_rowwise_2d
    # 3. remove predictions for the cached train set
    # 4. reshape output to the required m x h x k format
    def predict_rowwise(self, X):
        if X is None:
            raise ValueError(Messages.get_message(message_id="AUTOAITSLIBS0012E"))

        num_time_series = len(self.target_columns) if hasattr(self, "target_columns") else X.shape[1]
        # prepend last window of train set
        Xnew = np.concatenate((self.cached_last_window_train_set_, X), axis=0)
        # Xnew = self._input_data_transformation(Xnew)
        # call row prediction
        y_pred = self.predict_rowwise_2d(X=Xnew)
        # remove the prediction for the cached train set
        y_pred = y_pred[
            self.cached_last_window_train_set_.shape[0] :,
        ]
        # reshape to m x h x k, m is number of rows in input X, h is prediction horizon, k is number of time series
        y_pred = y_pred.reshape(y_pred.shape[0], -1, num_time_series)
        return y_pred

    # X: raw time series
    # This method returns the prediction for each row in X
    # We do not prepend last window of train set to X
    def predict_rowwise_2d(self, X):
        X = self._input_data_transformation(X)
        if self.row_mean_center:
            pipeline = self.regressor_
            if len(pipeline.steps) != 1:
                raise ValueError(Messages.get_message(message_id="AUTOAITSLIBS0013E"))

            # create a new transformer
            transformer = WindowTransformerMTS(lookback_window=self.lookback_window)
            # window and transform the data ONLY ONCE, right most column is latest in temporal order
            (Xw, _) = transformer.fit_transform(X)

            estimator = pipeline.steps[-1][
                -1
            ]  # take the final estimator of the pipeline
            y_pred = self._predict_rolling_recursive(
                X=Xw,
                model=estimator,
                remaining_prediction_horizon=self.prediction_horizon,
            )
        else:
            y_pred = self._predict_rolling(X)

        return y_pred

    # X is in windowed and unscaled space
    def _predict_rolling_recursive(self, X, model=None, remaining_prediction_horizon=0):
        # create a new transformer
        random_state = getattr(self, "random_state", None)
        rowmean_transformer = StandardRowMeanCenterMTS(
            lookback_window=self.lookback_window,
            random_state=random_state
        )
        # fit and transform X to the transformed space
        (Xt, _) = rowmean_transformer.fit_transform(X=X)
        # call 1-step ahead prediction, yt in scaled space
        yt = model.predict(Xt)
        if yt.ndim == 1:
            yt = yt.reshape(yt.shape[0], 1)

        # y_pred in raw space
        y_pred = rowmean_transformer.inverse_transform(yt)

        # replace previous columns with predicted columns
        for i in range(1, y_pred.shape[1]):
            X[:, i * self.lookback_window] = y_pred[:, i - 1]

        # remove the first column of X, append the last column of y_pred to right most of X
        X = np.concatenate((X[:, 1:], y_pred[:, -1].reshape(-1, 1)), axis=1)

        if remaining_prediction_horizon > 1:
            yp = self._predict_rolling_recursive(
                X=X,
                model=model,
                remaining_prediction_horizon=remaining_prediction_horizon - 1,
            )
            y_pred = np.concatenate((y_pred, yp), axis=1)

        return y_pred

    # X: raw time series
    def _predict_rolling(self, X):
        pipeline = self.regressor_
        # trained windowing transformer
        window_transformer = pipeline.steps[0][1]
        # trained final estimator
        estimator = pipeline.steps[-1][-1]
        # only window the data once, each row is one time step, right most side is latest in time
        Xt = window_transformer.transform(X)
        # calling imputer (if exists)
        Xt = pipeline.steps[1][1].transform(Xt)

        X4_svr = (
            Xt  # only use for SVR pipeline, keep a copy of windowed and unscaled data
        )

        y_pred = None
        # prediction, keep same rows, extending to the right
        for k in range(self.prediction_horizon):
            if "SVR" in self.short_name:  # scale data
                Xt = pipeline.steps[2][1].transform(X4_svr)

            # call 1-step ahead prediction
            yt = estimator.predict(Xt)
            if yt.ndim == 1:
                yt = yt.reshape(yt.shape[0], 1)
            # keep prediction results, for prediction horizon k
            if y_pred is None:
                y_pred = yt
            else:
                y_pred = np.concatenate((y_pred, yt), axis=1)

            # append predicted results to the right most columns, remove left most columns (older in time)
            # continue prediction for the same time step, using predicted values only
            # for each row, keep same ground-truth data during prediction
            if "SVR" in self.short_name:
                X4_svr = np.concatenate((X4_svr[:, yt.shape[1] :], yt), axis=1)
            else:
                Xt = np.concatenate((Xt[:, yt.shape[1] :], yt), axis=1)

        return y_pred

    # attempt to have a uniform interface for returning the internal estimator from our metaestimators
    @property
    def get_estimators(self):
        return [getattr(self, "regressor", None)]

