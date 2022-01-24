"""Provides a PyTorch-compatible dataset."""

from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
from torch.utils.data import Dataset

from forecast.data import (FUTURE_DEP_KEY, FUTURE_DEP_KEY_UTF, FUTURE_IND_KEY, FUTURE_IND_KEY_UTF,
                           PAST_DEP_KEY, PAST_DEP_KEY_UTF, PAST_IND_KEY, PAST_IND_KEY_UTF)
from .transforms import AbstractTransform, TSample


class TimeSeriesDataset(Dataset):
    """Provides a moving window view into a list of time series."""

    def __init__(self,
                 time_series: Union[np.ndarray, Sequence[np.ndarray]],
                 window_size: int,
                 forecast_horizon: int,
                 targets: List[int],
                 step: int = 1,
                 transform: Optional[AbstractTransform] = None,
                 future_regressors: Optional[List[int]] = None,
                 include_untransformed: bool = False):
        """Creates a time series dataset.

        Parameters
        ----------
        time_series: np.ndarray | Sequence[np.ndarray]
            List of time series arrays
        window_size: int
            Number of samples used as input for forecasting.
        forecast_horizon: int
            Number of samples to forecast.
        targets: List[int]
            A list of row indices of the forecast targets
        step: int
            Number of samples between consecutive examples from the same time series.
        transform: AbstractTransform, optional
            A transform to apply to the data (defaults to None)
        future_regressors: List[int], optional
            The future regressors available for prediction (defaults to all non-targets)
        include_untransformed: bool, optional
            Determines whether untransformed values are also included in a sample (default is False)

        """
        self._data = time_series
        self._window_size = window_size
        self._forecast_period = forecast_horizon
        self._full_sample_size = self._window_size + self._forecast_period
        self._step = step
        self.transform = transform

        # compute split the regressors from the targets
        self._targets = targets
        target_set = set(targets)
        self._regressors = [i for i in range(time_series[0].shape[0]) if i not in target_set]
        self._future_regressors = future_regressors if future_regressors else self._regressors
        self._include_utf = include_untransformed

        # store (ts_index, start_ind) in list
        # __getitem__ will use this to slice the cached TS data
        self._sample_ids: List[Tuple[int, int]] = []

        n_dropped = 0
        for i, ts in enumerate(self._data):
            # convert a single time series into a series of sequential samples
            if ts.shape[-1] < self._forecast_period:
                # we can't forecast N samples if we have < N samples to serve as ground truth
                n_dropped += 1
                continue
            elif ts.shape[-1] < self._full_sample_size:
                # If the time series is too short, we will zero pad the input
                # TODO: revisit whether we should pad
                num_examples = 1
            else:
                # truncate incomplete samples at the end
                num_examples = (ts.shape[-1] - self._full_sample_size + self._step) // self._step

            # store (ts_index, start_ind)
            for j in range(num_examples):
                self._sample_ids.append((i, j * self._step))

        # Inform user about time series that were too short
        if n_dropped > 0:
            print(f"Dropped {n_dropped} time series due to length.")

    def __len__(self) -> int:
        """Provides the length of the dataset.

        Returns
        -------
        int
            The number of examples in the dataset

        """
        return len(self._sample_ids)

    def __getitem__(self, idx: int) -> TSample:
        """Retrives an example from the dataset.

        Parameters
        ----------
        idx: int
            The index of the example to retrieve

        Returns
        -------
            The transformed sample

        """
        # Get time series
        ts_id, offset = self._sample_ids[idx]
        ts = self._data[ts_id]

        # Prepare input and target. Zero pad if necessary.
        if ts.shape[-1] < self._full_sample_size:
            # If the time series is too short, zero-pad on the left
            # TODO: revisit whether we should pad
            X_past = ts[self._regressors, :-self._forecast_period]
            X_past = np.pad(
                X_past,
                pad_width=((0, 0), (self._window_size - X_past.shape[-1], 0)),
                mode='constant',
                constant_values=0
            )
            y_past = ts[self._targets, :-self._forecast_period]
            y_past = np.pad(
                y_past,
                pad_width=((0, 0), (self._window_size - y_past.shape[-1], 0)),
                mode='constant',
                constant_values=0
            )

            X_fut = ts[self._future_regressors, -self._forecast_period:]
            y_fut = ts[self._targets, -self._forecast_period:]
        else:
            X_past = ts[self._regressors, offset:offset + self._window_size]
            y_past = ts[self._targets, offset:offset + self._window_size]
            X_fut = ts[self._future_regressors, offset + self._window_size:offset + self._full_sample_size]
            y_fut = ts[self._targets, offset + self._window_size:offset + self._full_sample_size]

        # Create the input and output for the sample
        # X_past: (num_features, window_size)
        # y_past: (num_targets, window_size)
        # X_fut: (num_fut_features, horizon)
        # y_fut: (num_targets, horizon)
        sample = {PAST_IND_KEY: X_past,
                  PAST_DEP_KEY: y_past,
                  FUTURE_IND_KEY: X_fut,
                  FUTURE_DEP_KEY: y_fut}

        if self.transform:
            sample = self.transform(sample)

        if self._include_utf:
            sample[PAST_IND_KEY_UTF] = X_past
            sample[PAST_DEP_KEY_UTF] = y_past
            sample[FUTURE_IND_KEY_UTF] = X_fut
            sample[FUTURE_DEP_KEY_UTF] = y_fut

        return sample
