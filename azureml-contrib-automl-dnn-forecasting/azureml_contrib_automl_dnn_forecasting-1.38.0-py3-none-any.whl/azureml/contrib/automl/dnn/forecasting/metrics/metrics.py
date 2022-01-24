# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for calculating metrices for forecast dnn training."""
import logging
import math
import numpy as np
from typing import Dict, Any, Union, List

import azureml.automl.core   # noqa: F401
from azureml.automl.core.shared import constants

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import (
    ClientException,
    DataException,
    InvalidOperationException,
    ValidationException
)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNMetricsCalculationError

from azureml.automl.runtime.shared import metrics as classical_metrics
from azureml.automl.runtime.shared.score.scoring import aggregate_scores
from azureml.automl.runtime.shared.score.constants import FORECASTING_SET, REGRESSION_SET
from azureml.automl.runtime.shared.metrics_utilities import compute_metrics

from azureml.automl.runtime.shared import _dataset_binning

from azureml.automl.core.shared import logging_utilities
from azureml.automl.runtime._metrics_logging import log_metrics
from ..constants import ForecastConstant
import Deep4Cast.deep4cast.metrics as forecast_metrics
from forecast.data import FUTURE_DEP_KEY

logger = logging.getLogger(__name__)


def _get_worst_scores(metric_names):
    epslon = 0.00001
    worst_scores = classical_metrics.get_worst_values(task=constants.Tasks.REGRESSION)
    metric_objectives = classical_metrics.get_default_metric_with_objective(task=constants.Tasks.REGRESSION)
    scores = {}
    for name in metric_names:
        if name in worst_scores:
            if np.isnan(worst_scores[name]):
                continue
            scores[name] = worst_scores[name]
            # Update the values to avoid the assert for worst values.
            if name in metric_objectives:
                if metric_objectives[name] == constants.OptimizerObjectives.MAXIMIZE:
                    scores[name] -= epslon
                else:
                    scores[name] += epslon
    return scores


def compute_metric(act: np.ndarray, pred: np.ndarray, metric: str) -> float:
    """Compute the passed  metric using automl metric module for early stopping by forecast module.

    Parameters
    ----------
    act: np.ndarray
        The target values (shape [1, batch_size * forecast_length])
    pred: np.ndarray
        The predicted values (shape [1, batch_size * forecast_length])
    metric: str
        metric to compute

    Returns
    -------
    float

    """
    try:
        return classical_metrics.compute_metrics(pred, act,
                                                 task=constants.Tasks.REGRESSION,
                                                 metrics=[metric])
    except (ValueError, DataException, ValidationException, InvalidOperationException) as e:
        if logger is not None:
            logging_utilities.log_traceback(e, logger)
        return _get_worst_scores([metric])


def compute_metrics_using_evalset(eval_set, y_pred, rethrow):
    """Compute metric using the _EvalDataset and return worst score or exception on metrics computation.

    :param eval_set: _EvalDataset for a grain for a slice.
    :param y_pred: an np arraay of prediction of the evaluation set.
    :param rethrow: whether to reraise the exception or produce worst score.
    """
    exception_raised = False
    try:
        scores = compute_metrics(eval_set.X_valid,
                                 eval_set.y_valid,
                                 eval_set.X_train,
                                 eval_set.y_train,
                                 y_pred,
                                 None,
                                 eval_set,
                                 constants.Tasks.REGRESSION,
                                 FORECASTING_SET | REGRESSION_SET)
    except InvalidOperationException as e:
        exception_raised = True
        logger.warning("Forecast Metric calculation resulted in error, reporting back worst scores")
        if rethrow:
            raise ClientException._with_error(
                AzureMLError.create(
                    TCNMetricsCalculationError, target="metrics",
                    reference_code=ReferenceCodes._TCN_METRICS_CALCULATION_ERROR_EVALSET,
                    inner_exception=e)
            ) from e
        scores = _get_worst_scores(FORECASTING_SET | REGRESSION_SET)
    return exception_raised, scores


def compute_metrics_using_pred_true(y_pred, y_true_forecast, horizon, scalar_only=True, rethrow: bool = False) \
        -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the classic and time series metric for the training.

    :param y_pred: forecasted target values.
    :param y_true_forecast: actual target values.
    :param horizon: horizon used for predictions.
    :param scalar_only: whether to compute scalar metrices only.
    :param rethrow: to rethrow execption from metrics computation.
    :return: scores dictionary.
    """
    y_true_classical = y_true_forecast.reshape(-1)
    y_pred_classical = y_pred.reshape(-1)
    bin_info = None
    metrics_to_compute = constants.Metric.SCALAR_REGRESSION_SET
    worst_scores = _get_worst_scores(metrics_to_compute)
    computed_scores = {}
    try:
        exception_raised = False
        if not scalar_only:
            bin_info = _dataset_binning.make_dataset_bins(y_true_classical.shape[0], y_true_classical)
            metrics_to_compute = constants.Metric.REGRESSION_SET

        computed_scores = classical_metrics.compute_metrics(y_pred_classical, y_true_classical,
                                                            task=constants.Tasks.REGRESSION,
                                                            metrics=metrics_to_compute,
                                                            bin_info=bin_info)

        # reshape prediction
        # Number of samples predicted per item based on the distribution
        number_of_samples_per_prediction = y_pred.shape[0]
        # Number of forecasting series to predict.
        number_of_items_to_predict = y_true_forecast.shape[0]
        # Number of target variables, we only support one dimensional y.
        number_of_target_variables = 1
        time_steps = horizon
        y_pred = y_pred.reshape(number_of_samples_per_prediction,
                                number_of_items_to_predict,
                                number_of_target_variables,
                                time_steps)
        computed_scores[constants.Metric.ForecastMAPE] = forecast_metrics.mape(y_pred, y_true_forecast).mean()

    except (ValueError, DataException, ValidationException, InvalidOperationException) as e:
        exception_raised = True
        logger.warning("Forecast Metric calculation resulted in error, reporting back worst scores")
        if rethrow:
            raise ClientException._with_error(
                AzureMLError.create(
                    TCNMetricsCalculationError, target="metrics",
                    reference_code=ReferenceCodes._TCN_METRICS_CALCULATION_ERROR,
                    inner_exception=e)
            ) from e
    for name in worst_scores:
        # if metric not in computed metrics, i.e an exception, the set the metric to be worst
        # if the metric is nan then replace it with worst score.
        if name not in computed_scores or math.isnan(computed_scores[name]):
            computed_scores[name] = worst_scores[name]
    return exception_raised, computed_scores


def get_target_values(model, ds_test):
    """Get target y values in dataloader indexed order."""
    ds_test._keep_untransformed = True
    y_true_forecast = []
    batch_size = model.params.get_value(ForecastConstant.Batch_size)
    dataloader = model.create_data_loader(ds_test, False, batch_size)
    for i, batch in enumerate(dataloader):
        if ds_test.has_past_regressors:
            y_true_forecast.append(batch[FUTURE_DEP_KEY].numpy())
        else:
            y_true_forecast.append(batch["y"].numpy())
    y_true_forecast = np.concatenate(y_true_forecast, axis=0)
    ds_test._keep_untransformed = False
    return y_true_forecast


def save_metric(run, scores):
    """
    Save the metrics into the run history/artifact store.

    :param run: azureml run context
    :param scores: dictionary of score name and values.
    :return: None
    """
    logger.info("Saving scores for the child run.")
    log_metrics(run, scores)


def compute_aggregate_score(cv_scores: List[Dict]):
    """
    Compoute the aggregate metrics from cross validation scores.

    :param cv_scores: List of cross validation scores
    :return: Dict of aggregate score
    """
    scores = cv_scores[0] if len(cv_scores) > 0 else {}
    exception_raised = False
    try:
        if len(cv_scores) > 1:
            scores = aggregate_scores(cv_scores, cv_scores[0].keys())
    except TypeError:
        exception_raised = True
    return exception_raised, scores


def get_scalar_only_scores(scores):
    """Get the scalar only metrics for saving at epoch level."""
    return {key: scores[key] for key in scores if np.isscalar(scores[key])}
