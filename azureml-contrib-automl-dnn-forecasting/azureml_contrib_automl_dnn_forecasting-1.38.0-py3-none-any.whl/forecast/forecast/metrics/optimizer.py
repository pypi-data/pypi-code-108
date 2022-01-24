"""Metrics related to the status of the optimizer."""
from typing import Mapping, Sequence

import numpy as np
import torch.optim

from forecast.metrics import Metric, MetricMode


class LearningRate(Metric):
    """Adds the current learning rate to the metrics passed to callbacks."""

    def __init__(self, opt: torch.optim.Optimizer, group_index: int = 0):
        """Adds the current learning rate of parameter group `index` to the metrics passed to callbacks."""
        super().__init__(MetricMode.TRAIN)
        self._opt = opt
        self._index = group_index

    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """No op."""
        pass

    def reset_state(self) -> None:
        """No op."""
        pass

    def result(self) -> float:
        """Returns the current learning rate.

        Returns
        -------
        float

        """
        return self._opt.param_groups[self._index]["lr"]
