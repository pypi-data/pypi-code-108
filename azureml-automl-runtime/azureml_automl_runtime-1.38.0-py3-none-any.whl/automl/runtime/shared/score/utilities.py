# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import numpy as np

from typing import Any, Dict, List, Optional, Tuple

from azureml.automl.runtime.shared.score import constants
from azureml.automl.core.shared.exceptions import ClientException


def get_metric_task(metric: str) -> str:
    """
    Get the task for a given metric.

    :param metric: The metric to lookup.
    :return: The task type for the given metric.
    """
    if metric in constants.CLASSIFICATION_SET:
        return constants.CLASSIFICATION
    elif metric in constants.REGRESSION_SET:
        return constants.REGRESSION
    elif metric in constants.FORECASTING_SET:
        return constants.FORECASTING
    raise ClientException("Metric {} not found".format(metric))


def minimize_or_maximize(metric: str,
                         task: Optional[str] = None) -> str:
    """
    Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        task = get_metric_task(metric)
    return constants.OBJECTIVES_TASK_MAP[task][metric]


def is_better(val1: float,
              val2: float,
              metric: Optional[str] = None,
              objective: Optional[str] = None) -> bool:
    """Select the best of two values given metric or objectives.

    :param val1: scalar value
    :param val2: scalar value
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :param objective: one of constants.OptimizerObjectives.
    return: returns a boolean of if val1 is better than val2 in the situation
    """
    if objective is None:
        if metric is None:
            raise ClientException("Must specific either metric or objective")
        else:
            objective = minimize_or_maximize(metric)
    if objective == constants.MAXIMIZE:
        return val1 > val2
    elif objective == constants.MINIMIZE:
        return val1 < val2
    return False


def get_all_nan(task: str) -> Dict[str, float]:
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    return {m: np.nan for m in constants.METRICS_TASK_MAP[task]}


def get_metric_ranges(task: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Get the metric range for the task.

    :param task: Machine learning task.
    :return: Tuple with dictionaries of minimum and maximum scores.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task)
    return minimums, maximums


def get_worst_values(task: str) -> Dict[str, float]:
    """
    Get the worst possible scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary from metric names to the worst scores.
    """
    minimums, maximums = get_metric_ranges(task)
    task_objectives = constants.OBJECTIVES_TASK_MAP[task]

    worst_scores = dict()
    for metric_name, objective in task_objectives.items():
        if metric_name == constants.TRAIN_TIME:
            worst_scores[metric_name] = constants.SCORE_UPPER_BOUND
            continue

        if objective == constants.MAXIMIZE:
            worst_scores[metric_name] = minimums[metric_name]
        else:
            worst_scores[metric_name] = maximums[metric_name]
    return worst_scores


def get_min_values(task: str) -> Dict[str, float]:
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: lower for metric_name, (lower, _) in task_ranges.items()}


def get_max_values(task: str) -> Dict[str, float]:
    """
    Get the maximum scores for metrics of the task.

    :param task: Machine learning task.
    :return: Dictionary of metrics with the maximum scores.
    """
    task_ranges = constants.RANGES_TASK_MAP[task]  # type: Dict[str, Tuple[float, float]]
    return {metric_name: upper for metric_name, (_, upper) in task_ranges.items()}


def assert_metrics_sane(scores: Dict[str, Any], task: str) -> None:
    """
    Assert that the given scores are within the valid range.

    This only checks the lower bound (upper for minimizing metrics).

    :param scores: Dictionary from metric name to metric score.
    :param task: Task name.
    """
    worst_scores = get_worst_values(task)
    objectives = constants.OBJECTIVES_TASK_MAP[task]
    for metric_name, score in scores.items():
        if not np.isscalar(score) or np.isnan(score):
            continue

        worst_value = worst_scores[metric_name]
        if objectives[metric_name] == constants.MAXIMIZE:
            if score < worst_value:
                message = "Score out of bounds for maximizing metric {}: {} < {}".format(
                    metric_name, score, worst_value)
                safe_message = "Score out of bounds for maximizing metric"
                raise ClientException(message).with_generic_msg(safe_message)
        elif objectives[metric_name] == constants.MINIMIZE:
            if score > worst_value:
                message = "Score out of bounds for minimizing metric {}: {} > {}".format(
                    metric_name, score, worst_value)
                safe_message = "Score out of bounds for minimizing metric"
                raise ClientException(message).with_generic_msg(safe_message)
        else:
            raise ClientException("Cannot validate metric bounds for metrics that are not minimizing or maximizing")


def get_scalar_metrics(task: str) -> List[str]:
    """Get the scalar metrics supported for a given task.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.CLASSIFICATION: list(constants.CLASSIFICATION_SCALAR_SET),
        constants.REGRESSION: list(constants.REGRESSION_SCALAR_SET),
        constants.FORECASTING: list(constants.FORECASTING_SCALAR_SET)
    }[task]


def get_default_metrics(task: str) -> List[str]:
    """Get the metrics supported for a given task as a set.

    :param task: Task string, (e.g. "classification" or "regression")
    :return: List of the default metrics supported for the task
    """
    return {
        constants.CLASSIFICATION: list(constants.CLASSIFICATION_SET
                                       - constants.UNSUPPORTED_CLASSIFICATION_TABULAR_SET),
        constants.REGRESSION: list(constants.REGRESSION_SET),
        constants.FORECASTING: list(constants.FORECASTING_SET)
    }[task]


def is_scalar(metric_name: str) -> bool:
    """
    Check whether a given metric is scalar or nonscalar.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    if metric_name in constants.FULL_SCALAR_SET or \
            metric_name in constants.CLASSIFICATION_MULTILABEL_SET:
        return True
    elif metric_name in constants.FULL_NONSCALAR_SET:
        return False
    elif metric_name in constants.CLASSIFICATION_CLASSWISE_SET:
        return False
    raise ClientException("{} metric is not supported".format(metric_name))


def is_classwise(metric_name: str) -> bool:
    """
    Check whether a given metric is a classwise metric.

    :param metric_name: the name of the metric found in constants.py
    :return: boolean for if the metric is scalar
    """
    if metric_name in constants.CLASSIFICATION_CLASSWISE_SET:
        return True
    else:
        return False
    raise ClientException("{} metric is not supported".format(metric_name))
