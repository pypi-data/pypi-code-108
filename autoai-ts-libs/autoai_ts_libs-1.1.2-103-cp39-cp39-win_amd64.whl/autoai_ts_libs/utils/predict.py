# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2021, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

import logging
logger = logging.getLogger(__name__)
logger.setLevel('WARNING')
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline

from autoai_ts_libs.srom.estimators.time_series.models.base import (
    SROMTimeSeriesForecaster,
)
from autoai_ts_libs.srom.estimators.time_series.models.srom_estimators import (
    SROMTimeSeriesEstimator,
)
from autoai_ts_libs.watfore.watfore_forecasters import (
    WatForeForecaster as tslibs_watfore_forecasters,
)

from autoai_ts_libs.sklearn.mvp_windowed_transformed_target_estimators import (
    AutoaiWindowTransformedTargetRegressor,
)
from sklearn.metrics._scorer import _BaseScorer
from lale.operators import TrainablePipeline
from lale.operators import TrainedPipeline

from autoai_ts_libs.utils.score import Score
class _PredictScorer(_BaseScorer):
    def _score(self, method_caller, estimator, X, y_true, sample_weight=None):
        """Evaluate predicted target values for X relative to y_true.

        Parameters
        ----------
        method_caller : callable
            Returns predictions given an estimator, method name, and other
            arguments, potentially caching results.

        estimator : object
            Trained estimator to use for scoring. Must have a predict_proba
            method; the output of that is used to compute the score.

        X : array-like or sparse matrix
            Test data that will be fed to estimator.predict.

        y_true : array-like
            Gold standard target values for X.

        sample_weight : array-like, optional (default=None)
            Sample weights.

        Returns
        -------
        score : float
            Score function applied to prediction of estimator on X.
        """

        (y_test_stats, y_pred_score_stats) = Predict.predict_and_adjust_by_imputation_mask(estimator, X, y_true)

        return self._sign * self._score_func(y_test_stats, y_pred_score_stats,
                                                 **self._kwargs)

class Predict:
    @classmethod
    def predict_and_adjust_by_imputation_mask(cls, m, X_test, y_test):
        """
        Predict method called on the chosen fetched pipeline.

        Parameters
        ----------
        m: the pipeline, required
        X_test: numpy.ndarray, required
            Test data for prediction
        y_test: numpy.ndarray, required
            real y test data

        Returns
        -------
        y_test_list and y_predict_list:
            The y true values list and y predict values list.
        """
        ho_size, dDim = y_test.shape
        prediction_horizon = Score.get_prediction_win(m)
        lookback_window = len(X_test) - len(y_test)
        # UTS_1S MTS_1S:
        estimator = Score.get_estimator(m)
        if isinstance(estimator, TrainablePipeline) or isinstance(estimator, TrainedPipeline):
            estimator = estimator._final_estimator
        if prediction_horizon == 1:
            try:
                non_autoai_core_pl = (
                        (hasattr(estimator, "name") and estimator.name() == "WatForeForecaster")
                        or (hasattr(estimator, "name") and estimator.name() == "WatForeTimeSeriesJointOptimizer")
                        or isinstance(estimator, tslibs_watfore_forecasters)
                        or isinstance(estimator, SROMTimeSeriesForecaster)
                )
                if non_autoai_core_pl:
                    y_pred = m.predict(
                        X_test[lookback_window:, ],
                        prediction_type=Score.PREDICT_SLIDING_WINDOW,
                    )
                elif isinstance(
                        estimator, SROMTimeSeriesEstimator
                ):  # Stateless
                    y_pred = m.predict(X_test, prediction_type=Score.PREDICT_SLIDING_WINDOW)[
                             lookback_window:
                             ]
                elif isinstance(
                        estimator, AutoaiWindowTransformedTargetRegressor
                ) or (isinstance(m, Pipeline) and not non_autoai_core_pl):
                    # (1) X_test as received has the lookback_window from the end of the training set prepended
                    # (2) the last (prediction_horizon, currently 1) values of y_pred have no test values to compare to, so take -prediction_horizon
                    # (3) the first element in y_test is covered by the last prepend window in X_test, so take -1 from lookback_window
                    y_pred = m.predict(X=X_test, prediction_type="rowwise_2d")[
                             lookback_window - 1: -prediction_horizon
                             ]  # TODO: Double check alignment
                else:
                    print("Unknown Pipeline Type" + m)
                    y_pred = None

            except Exception as e:
                y_pred = None
                raise e
        # UTS_MSxx MTS_MSxx:
        elif prediction_horizon > 1:
            try:
                if (
                        ho_size < prediction_horizon
                ):  # if prediction horizon goes beyond hold out
                    ph = ho_size

                # y_pred as output from each of 10 pipelines
                non_autoai_core_pl = (
                        (hasattr(estimator, "name") and estimator.name() == "WatForeForecaster")
                        or (hasattr(estimator, "name") and estimator.name() == "WatForeTimeSeriesJointOptimizer")
                        or isinstance(estimator, tslibs_watfore_forecasters)
                        or isinstance(estimator, SROMTimeSeriesForecaster)
                )
                if non_autoai_core_pl:
                    if ho_size < prediction_horizon and isinstance(
                            estimator, SROMTimeSeriesForecaster
                    ):
                        y_pred = m.predict(X_test[lookback_window:, ])
                    else:
                        # y_pred = m.predict_multi_step_sliding_window(
                        #   X_test[self.dobj.lookback_window :,], prediction_horizon
                        if isinstance(estimator, SROMTimeSeriesForecaster):
                            y_pred = m.predict(
                                X_test[lookback_window:, ],
                                prediction_type=Score.PREDICT_SLIDING_WINDOW,
                            )
                        else:
                            y_pred = m.predict(
                                X_test[lookback_window:, ],
                                prediction_horizon=prediction_horizon,
                                prediction_type=Score.PREDICT_SLIDING_WINDOW,
                            )  # TODO: Double check alignment

                    if isinstance(estimator, SROMTimeSeriesForecaster):
                        y_pred = y_pred.flatten()
                    else:
                        y_pred = np.array(y_pred).flatten()  # temporary fix

                elif isinstance(
                        estimator, SROMTimeSeriesEstimator
                ):  # Stateless
                    if ho_size < prediction_horizon:
                        y_pred = m.predict(X_test)
                    else:
                        y_pred = m.predict(X_test, prediction_type=Score.PREDICT_SLIDING_WINDOW)

                    y_pred = y_pred.flatten()

                elif isinstance(
                        estimator, AutoaiWindowTransformedTargetRegressor
                ) or (isinstance(m, Pipeline) and not non_autoai_core_pl):
                    # (1) X_test as received has the lookback_window from the end of the training set prepended
                    # (2) the last (prediction_horizon, currently 1) values of y_pred have no test values to compare to, so take -prediction_horizon
                    # (3) the first element in y_test is covered by the last prepend window in X_test, so take -1 from lookback_window
                    if ho_size < prediction_horizon:
                        # y_pred = m.steps[0][1]._final_estimator.forecasts_
                        y_pred = m.predict(X=X_test, prediction_type="rowwise_2d")[
                            lookback_window - 1,
                        ]
                    else:
                        y_pred = m.predict(X=X_test, prediction_type='rowwise_2d')[
                                 lookback_window - 1: -prediction_horizon,
                                 ]

                    y_pred = y_pred.flatten()
                elif isinstance(m, SROMTimeSeriesEstimator):  # Stateless
                    if ho_size < prediction_horizon:
                        y_pred = m.predict(X_test)
                    else:
                        y_pred = m.predict_multi_step_sliding_window(X_test)

                    y_pred = y_pred.flatten()
                else:
                    print("Unknown Pipeline Type" + m)
                    y_pred = None
            except Exception as e:
                y_pred = None
                raise e
        # m.steps[0][1]._final_estimator.forecasts_
        # make a separate y_pred for scoring in case prediciton horizon > holdout
        # Subset to holdout size and use this for scoring as y_pred is written to files
        if ho_size < prediction_horizon:  # nothing to do
            y_pred_score = cls._trim_pred_vals(
                y_pred, ho_size, prediction_horizon, dDim
            )
        else:
            y_pred_score = y_pred

        if isinstance(y_pred, list):
            y_pred = np.asarray(y_pred)
        if isinstance(y_pred_score, list):
            y_pred_score = np.asarray(y_pred_score)

        y_pred_score = cls.adjust_prediction(
            y_test, y_pred_score.reshape(-1, y_test.shape[1]), ph=prediction_horizon
        )
        y_test_stats = y_test
        y_pred_score_stats = y_pred_score

        return (y_test_stats, y_pred_score_stats)

    @classmethod
    def adjust_prediction(cls, y, y_pred, ph):
        if (isinstance(y, list)):
            column_is_target = False
            number_targets = len(y)
        else:
            column_is_target = True
            number_targets = y.shape[1]

        y_pred_avg = None
        for i in range(number_targets):  # one TS
            if (column_is_target):
                y1D, y_pred1D = y[:, i].reshape(-1, 1), y_pred[:, i].reshape(-1, 1)
            else:
                y1D, y_pred1D = y[i].reshape(-1, 1), y_pred[i].reshape(-1, 1)

            # reset ph = len(y) if ph was chosen larger than the holdout set
            update_ph = ph
            if update_ph > y1D.shape[0]: update_ph = y1D.shape[0]

            y_pred1D_avg = cls.__compute_on_one_series(y_pred1D, update_ph)

            if i == 0:
                if (column_is_target):
                    y_pred_avg = y_pred1D_avg
                else:
                    y_pred_avg = []
                    y_pred_avg.append(y_pred1D_avg)
            else:
                if (column_is_target):
                    y_pred_avg = np.column_stack((y_pred_avg, y_pred1D_avg))
                else:

                    y_pred_avg.append(y_pred1D_avg)

        return y_pred_avg

    @classmethod
    def __compute_on_one_series(cls, y_pred1D, ph):
        y_pred1D = y_pred1D.reshape(-1, ph)
        y_pred_list = y_pred1D.tolist()

        yp = []
        for i in range(len(y_pred_list)):
            ynan = np.empty((i))
            ynan[:] = np.nan
            ynan = ynan.tolist()
            ynan.extend(y_pred_list[i])
            yp.append(ynan)

        # convert to dataframe to compute column-wise average
        df = pd.DataFrame(data=yp, index=None)

        y_pred1D_avg = df.mean(axis=0, skipna=None)
        y_pred1D_avg = np.asarray(y_pred1D_avg).reshape(-1, 1)

        return y_pred1D_avg

    @classmethod
    def _trim_pred_vals(
            cls, predicted_vals, holdout_size, prediction_horizon, num_dims
    ):

        if prediction_horizon <= holdout_size:  # nothing to do
            return predicted_vals

        # holdout_pred_diff =  prediction_horizon - holdout_size
        pr_vals = []
        itr = 0
        for i in range(0, num_dims):
            pr_vals.extend(
                predicted_vals[itr: itr + holdout_size]
            )  # trim each dimension individually
            itr = itr + prediction_horizon  # holdout_size+holdout_pred_diff

        predicted_vals = np.reshape(np.array(pr_vals), (-1,))
        return predicted_vals

    @classmethod
    def _adjust_y_test_y_pred_by_imputation_mask(cls, y_test, y_predict):
        """Adjust y_test and y_predict by imputation_mask.

        Parameters
        ----------
        y_test : array-like or sparse matrix
            Test data that will be fed to estimator.predict.

        y_predict : array-like
            Gold standard target values for X.

        Returns
        -------
        score : y_test_list and y_predict_list
            Adjust y_test and y_predict.
        """
        imputation_mask = np.isnan(y_test)
        number_targets = y_test.shape[1]
        y_test_list = []
        y_predict_list = []
        if number_targets == 1:
            imputed_value_index = np.where(imputation_mask == 0)
            if (len(y_test) != len(y_predict) or len(imputed_value_index[0]) == 0):
                return None, None
            y_test = np.reshape(y_test[imputed_value_index], (-1, 1))
            y_predict = np.reshape(y_predict[imputed_value_index], (-1, 1))
            y_test_list.append(y_test)
            y_predict_list.append(y_predict)
        else:
            if (len(y_test) != len(y_predict)):
                y_predict = y_predict.reshape(-1, y_test.shape[1])

            for i in range(number_targets):
                imputed_value_index = np.where(imputation_mask[:, i] == 0)
                current_y_test = y_test[:, i]
                current_y_predict = y_predict[:, i]
                if (len(current_y_test) != len(current_y_predict)) or len(imputed_value_index[0]) == 0:
                    return None, None
                current_y_test = current_y_test[imputed_value_index]
                current_y_predict = current_y_predict[imputed_value_index]
                y_test_list.append(current_y_test)
                y_predict_list.append(current_y_predict)
        return y_test_list, y_predict_list