"""The base class from which all metrics are derived."""

import abc
import enum
from typing import Mapping, Sequence

import numpy as np


class MetricMode(enum.Enum):
    """Determines on which subsets of data (e.g., train, val, etc) a metric should be computed."""

    TRAIN = enum.auto()  # the metric will only be computed on training data
    VAL = enum.auto()  # the metric will only be computed on validation data
    TRAIN_VAL = enum.auto()  # the metric will be computed on training and validation data


class Metric(abc.ABC):
    """The base class from which all metrics are derived."""

    def __init__(self, mode: MetricMode):
        """Instantiates a metric which will be computed during training, validation, or both.

        Parameters:
        -----------
        mode: MetricMode
            Determines whether the metric is computed during training, validation, or both

        """
        super().__init__()
        self._computed_on_train = True if mode in (MetricMode.TRAIN, MetricMode.TRAIN_VAL) else False
        self._computed_on_val = True if mode in (MetricMode.VAL, MetricMode.TRAIN_VAL) else False

    @abc.abstractmethod
    def update_state(self, inputs: Mapping[str, np.ndarray], act: np.ndarray, pred: Sequence[np.ndarray]) -> None:
        """Metrics implement this function to update their state in a streaming fashion.

        Parameters
        ----------
        inputs: Mapping[str, np.ndarrary]
            The input passed to the model with all tensors converted to numpy arrays
        act: np.ndarray
            The target values for the model to forecast (shape [batch_size, forecast_length])
        pred: Sequence[np.ndarray]
            The values the model forecasted (shape [pred_index][batch_size, forecast_length])

        Returns
        -------
        None

        """
        raise NotImplementedError

    @abc.abstractmethod
    def reset_state(self) -> None:
        """Resets the state of a metric at the end of an epoch.

        Returns:
        --------
        None

        """
        raise NotImplementedError

    @abc.abstractmethod
    def result(self) -> float:
        """Returns the metric's value."""
        raise NotImplementedError

    @property
    def computed_on_train(self) -> bool:
        """Should the metric be evaluated on training data."""
        return self._computed_on_train

    @property
    def computed_on_val(self) -> bool:
        """Should the metric be evaluated on validation data."""
        return self._computed_on_val
