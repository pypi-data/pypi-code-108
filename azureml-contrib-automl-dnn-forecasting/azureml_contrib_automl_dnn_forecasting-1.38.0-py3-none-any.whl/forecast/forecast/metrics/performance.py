"""Computes various metrics evaluating forecasting model performance."""
from typing import Mapping, Sequence

import numpy as np

from forecast.metrics import Metric, MetricMode


class SMAPE(Metric):
    """Computes the symmetric mean absolute percent error as a fraction, NOT a percentage."""

    def __init__(self, index: int, mode: MetricMode):
        """Computes the symmetric mean absolute percent error as a fraction, NOT a percentage.

        Parameters
        ----------
        index: int
            The index in the forecast_head axis of the quantity to compare to the target
        mode: MetricMode
            Which datasets the metric should be computed on

        """
        super().__init__(mode)
        self._index = index
        self._tot = self._count = 0.
        self.reset_state()

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """Updates the streaming SMAPE state.

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
        self._tot += np.sum(np.abs(pred - act) / (np.abs(pred) + np.abs(act)))
        self._count += len(pred)

    def reset_state(self) -> None:
        """Resets the state of SMAPE at the end of an epoch.

        Returns
        -------
        None

        """
        self._count = 0.
        self._tot = 0.

    def result(self) -> float:
        """Computes the SMAPE over the last epoch.

        Returns
        -------
        float

        """
        return 2 * self._tot / self._count
