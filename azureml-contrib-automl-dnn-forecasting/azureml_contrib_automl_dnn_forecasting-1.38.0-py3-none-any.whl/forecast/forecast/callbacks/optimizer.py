"""Callbacks which integrate with and/or modify the behavior of model optimizers."""

import datetime
import math
from typing import Callable, Mapping, Optional

from torch.optim.lr_scheduler import _LRScheduler, ReduceLROnPlateau
from typing_extensions import Literal

from forecast.callbacks import Callback
from forecast.utils import EarlyTerminationException


class LRScheduleCallback(Callback):
    """Wraps a generic learning rate schedule in a callback."""

    def __init__(self, sched: _LRScheduler):
        """Wraps a generic learning rate schedule in a callback.

        Parameters
        ----------
        sched: _LRScheduler
            A learning rate scheduler which only requires the current epoch to step

        """
        super().__init__()
        self._sched = sched

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Steps the learning rate scheduler.

        Parameters
        ----------
        epoch: int
            The current epoch

        Returns
        -------
        None

        """
        self._sched.step(epoch)


class ReduceLROnPlateauCallback(Callback):
    """Wraps a ReduceLROnPlateau schedule in a callback."""

    def __init__(self, sched: ReduceLROnPlateau, metric_name: str):
        """Wraps a ReduceLROnPlateau schedule in a callback.

        Parameters
        ----------
        sched: ReduceLROnPlateau
            The learning rate schedule
        metric_name: str
            The name of the metric to be examined for plateau (or 'loss' if the loss function should be monitored)

        """
        super().__init__()
        self._sched = sched
        self._metric_name = metric_name

    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Examines whether the specified metric has plateaued.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The current value of the loss
        metrics: Mapping[str, float]
            The model's performance on the validation set during the current epoch

        Returns
        -------
        None

        """
        if self._metric_name == 'loss':
            m = loss
        else:
            m = metrics[self._metric_name]
        self._sched.step(m, epoch)


class EarlyStoppingCallback(Callback):
    """Terminates training early if the specified metric continually fails to improve."""

    def __init__(
            self,
            patience: int,
            min_improvement: float,
            metric: Optional[str] = None,
            mode: Literal["min", "max"] = 'min',
            improvement_type: Literal["relative", "absolute"] = 'relative',
            callback: Optional[Callable[[int, float, float], None]] = None,
    ):
        """Prematurely ends the training regimen in the val loss doesn't improve for a fixed number of epochs.

        Parameters
        ----------
        patience: int
            The number of epochs to wait for improvement before forcing termiantion
        min_improvement: float
            The size of the improvement required to be marked as a "realized" improvement
        metric: Optional[str]
            If None, uses the val loss to assess improvement. Otherwise, uses the specified metric. Defaults to None.
        mode: Literal["min", "max"]
            Whether the target value should decrease or increase in value. Defaults to min.
        improvement_type: Literal["relative", "absolute"]
            Whether the min_improvement specifies an absolute improvement value or a percent improvement. Defaults to
            relative.
        callback: Optional[Callback[[int, float, float], None]]
            A callback to be invoked upon the last computation of the validation metric prior to early termination. Is
            passed the epoch, current metric value, and best metric value. If None is supplied, no callback is invoked.
            Defaults to None.
        """
        super().__init__()

        if patience < 0:
            raise ValueError("Parameter `patience` must be >= 0.")
        if min_improvement < 0:
            raise ValueError("Parameter `min_improvement` must be >= 0.")

        self.patience = patience
        self.steps_since_improvement = 0
        self.metric = metric
        self._callback = callback
        self._terminate = False

        mode = mode.lower()
        if mode not in ('min', 'max'):
            raise ValueError('Parameter `mode` must be one of ("min", "max").')
        self.mode = mode
        self.best_score = float('inf') if self.mode == "min" else float("-inf")
        if self.mode == "min":
            min_improvement *= -1

        improvement_type = improvement_type.lower()
        if improvement_type not in ('relative', 'absolute'):
            raise ValueError('Parameter `improvement_type` must be one of ("relative", "absolute").')
        self.improvement_type = improvement_type
        if self.improvement_type == "relative":
            min_improvement += 1

        self.min_improvement = min_improvement

    def _get_thresh(self) -> float:
        if self.improvement_type == "relative":
            return self.best_score * self.min_improvement
        else:
            return self.best_score + self.min_improvement

    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Determines whether the validation metric has improved.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The current validation loss
        metrics: Mapping[str, float]
            A set of user-defined metrics evaluated every pass through the validation set

        Returns
        -------
        None

        """
        score = loss if self.metric is None else metrics[self.metric]
        thresh = self._get_thresh()
        improved = score < thresh if self.mode == "min" else score > thresh

        if improved:
            self.steps_since_improvement = 0
            self.best_score = score
        else:
            self.steps_since_improvement += 1

        if self.steps_since_improvement >= self.patience:
            if self._callback:
                self._callback(epoch, score, self.best_score)
            self._terminate = True

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Terminates training if appropriate by raising an EarlyTerminationException."""
        if self._terminate:
            raise EarlyTerminationException


class MaxTrainingTimeCallback(Callback):
    """Terminates training after a pre-specified amount of time."""

    def __init__(self, max_time: float):
        """The max amount of time, in seconds, for which training can run."""
        super().__init__()
        self._max_time = datetime.timedelta(seconds=max_time)
        self._start = None

    def on_train_begin(self) -> None:
        """Stores the start time when training begins."""
        self._start = datetime.datetime.now()

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Terminates training if our time budget has been consumed."""
        if datetime.datetime.now() - self._start > self._max_time:
            raise EarlyTerminationException


class PreemptTimeLimitCallback(Callback):
    """Terminates training prior to reaching a predeterminted time limit."""

    def __init__(self, end_time: datetime.datetime, margin: float = 0.1):
        """Creates a callback which terminates if the next epoch may potentially timeout.

        Parameters
        ----------
        end_time: datetime
            The time at which the experiment will timeout
        margin: float, optional
            How much buffer to permit, defaults to 0.1. A margin of X implies the experiment will terminate if
            (1+X) * last_epoch_time will exceed the time remaining.
        """
        super().__init__()
        self._tz = end_time.tzinfo  # capture timezone from supplied end time and use it when fetching time elsewhere
        now = datetime.datetime.now(self._tz)
        if end_time < now:
            raise ValueError(f"`end_time` cannot be in the past; received {end_time} but it's currently {now}")
        if margin < 0:
            raise ValueError(f"`margin` must be >= 0; received {margin}")

        self._end_time = end_time
        self._margin = margin
        self._epoch_start_time = None

    def on_train_epoch_begin(self, epoch: int) -> None:
        """Updates the epoch start time."""
        self._epoch_start_time = datetime.datetime.now(self._tz)

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Determines whether the training should be terminated at the end of the epoch."""
        now = datetime.datetime.now(self._tz)
        if (now - self._epoch_start_time) * (1 + self._margin) + now > self._end_time:
            raise EarlyTerminationException
        self._epoch_start_time = now


class NotFiniteTrainingLossCallback(Callback):
    """Terminates training if N consecutive training batches have a NaN/Inf/-Inf loss."""

    def __init__(self, num_non_finite: int):
        """Terminates training if num_non_finite consecutive training batches have a NaN/Inf/-Inf loss.

        Parameters
        ----------
        num_non_finite: int
            The number of non-finite batch losses to allow before termination.
        """
        super().__init__()
        if num_non_finite < 0:
            raise ValueError(f"`num_nans` must be > 0; received {num_non_finite}")
        self._max_bad = num_non_finite
        self._cur_bad = 0

    def on_train_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Determines at the end of every batch whether to terminate training.

        Parameters
        ----------
        epoch: int
            The training epoch
        batch: int
            The batch index
        loss: float
            The batch loss

        Returns
        -------
        None
        """
        is_finite = math.isfinite(loss)
        if is_finite:
            self._cur_bad = 0
        else:
            self._cur_bad += 1
        if self._cur_bad >= self._max_bad:
            raise EarlyTerminationException
