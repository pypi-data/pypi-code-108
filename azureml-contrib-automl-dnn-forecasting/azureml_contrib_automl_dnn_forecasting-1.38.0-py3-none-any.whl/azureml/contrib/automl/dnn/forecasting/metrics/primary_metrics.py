# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computes various metrics evaluating forecasting model performance."""
from typing import Mapping, Sequence

import numpy as np

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.runtime.shared import metrics as classical_metrics

from ..constants import ForecastConstant
from forecast.metrics import Metric, MetricMode
from .metrics import compute_metric


class NormalizedMetric(Metric):
    """Compute the primary metric."""

    def __init__(self, index: int, mode: MetricMode, primary_metric: str, default_score: float):
        """Compute normalized metric using automl metric module.

        Parameters
        ----------
        index: int
            The index in the forecast_head axis of the quantity to compare to the target
        mode: MetricMode
            Which datasets the metric should be computed on
        primary_metric: str
            Which primary metric to compute.
        default_score: float
            default_score to return when there is an error in computation.

        """
        super().__init__(mode)
        self._index = index
        self.primary_metric = primary_metric
        self.default_score = default_score

        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """Update the data for the state.

        Parameters
        ----------
        inputs: Mapping[str, np.ndarray]
            Unused
        act: np.ndarray
            The target values (shape [batch_size, forecast_length])
        pred: Sequence[np.ndarray]
            The predicted values (shape [forecast_heads][batch_size, forecast_length])

        Returns
        -------
        None

        """
        pred = pred[self._index].reshape(-1)
        act = act.reshape(-1)
        self._pred += list(pred)
        self._act += list(act)

    def reset_state(self) -> None:
        """Reset the state of Metric at the end of an epoch.

        Returns
        -------
        None

        """
        self._act = []
        self._pred = []

    def result(self) -> float:
        """Compute the metric over the last epoch.

        Returns
        -------
        float

        """
        pred = np.asanyarray(self._pred)
        act = np.asanyarray(self._act)
        try:
            metric = compute_metric(pred, act, self.primary_metric)[self.primary_metric]
            return float(metric)
        except (TypeError, ValueError, DataException, ValidationException):
            return self.default_score


class NRMSE(NormalizedMetric):
    """Compute the Normalized Mean Squared Error."""

    def __init__(self, index: int, mode: MetricMode):
        """Compute normalized root mean squared error.

        Parameters
        ----------
        index: int
            The index in the forecast_head axis of the quantity to compare to the target
        mode: MetricMode
            Which datasets the metric should be computed on

        """
        super().__init__(index, mode, ForecastConstant.NRMSE, float('inf'))
        self._index = index
        self.reset_state()


class NMAE(NormalizedMetric):
    """Compute the normalized mean absolute error."""

    def __init__(self, index: int, mode: MetricMode):
        """Compute normalized mean absolute error.

        Parameters
        ----------
        index: int
            The index in the forecast_head axis of the quantity to compare to the target
        mode: MetricMode
            Which datasets the metric should be computed on

        """
        super().__init__(index, mode, ForecastConstant.NRMAE, float('inf'))
        self._index = index
        self.reset_state()


class SpearmanCorrelation(NormalizedMetric):
    """Compute the Spearman Correlation."""

    def __init__(self, index: int, mode: MetricMode):
        """Compute normalized Spearman Correlatio.

        Parameters
        ----------
        index: int
            The index in the forecast_head axis of the quantity to compare to the target
        mode: MetricMode
            Which datasets the metric should be computed on

        """
        super().__init__(index, mode, 'spearman_correlation', float('-inf'))
        self._index = index
        self.reset_state()


def get_supported_metrics():
    """Get metrices supported for early stopping.

    Returns
    -------
    dictionary

    """
    mode = MetricMode.TRAIN_VAL
    return {
        ForecastConstant.NRMSE: NRMSE(ForecastConstant.MEDIAN_PREDICTION_INDEX, mode),
        ForecastConstant.NRMAE: NMAE(ForecastConstant.MEDIAN_PREDICTION_INDEX, mode)}
