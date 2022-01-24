"""Subtracts the last value of past_regressand from past/future regressands to eliminate the offset."""

import copy
import dataclasses as dc
from typing import Mapping, Sequence, Union

import torch

from forecast.data import FUTURE_DEP_KEY, PAST_DEP_KEY
from forecast.data.batch_transforms.common import BatchType


@dc.dataclass
class BatchSubtractOffset:
    """Subtracts the last value of past_regressand from past/future regressands to eliminate the offset.

    Attributes
    ----------
    index_mapping: Union[int, Sequence[int], Mapping[int, int]]
        The indices of the regressand series to be subtract. There are three use cases:
            - type int: a single regressand with the same feature index in past/future
            - type Sequence[int]: 1+ regressands with the same feature indices in past/future
            - type Mapping[int, int]: 1+ regressands with _different_ feature indices in past/future

        The last use case is somewhat rare, but may be encountered when historical data is unavailable.
    """

    index_mapping: Union[int, Sequence[int], Mapping[int, int]]

    def __post_init__(self):
        """Validates BatchSubtractOffset."""
        if isinstance(self.index_mapping, int):
            self.index_mapping = {self.index_mapping: self.index_mapping}
        elif isinstance(self.index_mapping, Sequence) and self.index_mapping:
            self.index_mapping = {i: i for i in self.index_mapping}
        elif isinstance(self.index_mapping, Mapping) and self.index_mapping:
            self.index_mapping = {k: v for k, v in self.index_mapping.items()}
        else:
            raise ValueError(f"Cannot convert index_mapping ({self.index_mapping}) to dict")
        self._past_indices = list(self.index_mapping.keys())
        self._future_indices = list(self.index_mapping.values())
        self._offset_key = "BATCH_OFFSET"

    def do(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Subtract the offset from the past/future regressands.

        Parameters
        ----------
        batch: BatchType
            The batch whose regressands will have their offset removed
        inplace: bool, optional
            Should the operation be performed in place, defaults to False.

        Returns
        -------
        BatchType
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)
            out[PAST_DEP_KEY] = out[PAST_DEP_KEY].detach().clone()
            if FUTURE_DEP_KEY in out:
                out[FUTURE_DEP_KEY] = out[FUTURE_DEP_KEY].detach().clone()

        last_val = out[PAST_DEP_KEY][:, self._past_indices, -1].unsqueeze(-1)
        out[PAST_DEP_KEY][:, self._past_indices, :] -= last_val
        if FUTURE_DEP_KEY in out:
            out[FUTURE_DEP_KEY][:, self._future_indices, :] -= last_val
        out[self._offset_key] = last_val
        return out

    def undo(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Restores the offset to the past/future regressands.

        Parameters
        ----------
        batch: BatchType
            The batch whose regressands will have their offset restored
        inplace: bool, optional
            Should the operation be performed in place, defaults to False.

        Returns
        -------
        BatchType
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)
            out[PAST_DEP_KEY] = out[PAST_DEP_KEY].detach().clone()
            if FUTURE_DEP_KEY in out:
                out[FUTURE_DEP_KEY] = out[FUTURE_DEP_KEY].detach().clone()

        if self._offset_key not in batch:
            raise ValueError(f"Cannot undo as batch is missing {self._offset_key}")
        last_val = out[self._offset_key]

        out[PAST_DEP_KEY][:, self._past_indices, :] += last_val
        if FUTURE_DEP_KEY in out:
            out[FUTURE_DEP_KEY][:, self._future_indices, :] += last_val
        return out

    def undo_y(self, y: torch.Tensor, batch: BatchType, *, inplace: bool = False) -> torch.Tensor:
        """Restores the offset to the regressand.

        Parameters
        ----------
        y: torch.Tensor
            The series which will have the offset restored
        batch: BatchType
            The batch whose regressands previously had their offset removed
        inplace: bool, optional
            Should the operation be performed in place, defaults to False.

        Returns
        -------
        torch.Tensor
        """
        if inplace:
            out = y
        else:
            out = y.detach().clone()

        if self._offset_key not in batch:
            raise ValueError(f"Cannot undo as batch is missing {self._offset_key}")
        out[:, self._future_indices, :] += batch[self._offset_key]
        return out
