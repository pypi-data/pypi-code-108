"""Applies one-hot encoding to the past and future regressors."""

import copy
import dataclasses as dc
from typing import Optional, Sequence, Union

import torch
import torch.nn.functional as F

from forecast.data import FUTURE_IND_KEY, PAST_IND_KEY
from forecast.data.batch_transforms.common import BatchType, make_int_list, within_range


@dc.dataclass
class OneHotEncoder:
    """Applies one-hot encoding to label-encoded features in a tensor.

    Attributes
    ----------
    feature_indices: Union[int, Sequence[int]]
    cardinality: Union[int, Sequence[int]]
    """

    feature_indices: Union[int, Sequence[int]]
    cardinality: Union[int, Sequence[int]]

    def __post_init__(self):
        """Validates the one-hot encoding."""
        self.feature_indices = make_int_list(self.feature_indices)
        self.cardinality = make_int_list(self.cardinality)

        num_feat = len(self.feature_indices)
        num_card = len(self.cardinality)
        if num_feat != num_card:
            raise ValueError(f"Number of feature indices ({num_feat}) must match cardinalities provided ({num_card})")
        elif num_feat == 0:
            raise ValueError("Must have at least one encoding specified.")

        if not within_range(self.feature_indices, 0):
            raise ValueError("Feature indices must all be positive.")
        if not within_range(self.cardinality, 2):
            raise ValueError("Cardinality for encoding must be >= 2.")

    def encode(self, tensor: torch.Tensor) -> torch.Tensor:
        """Applies the one-hot encoding to label-encoded features.

        Parameters
        ----------
        tensor: torch.Tensor
            The tensor which contains one or more label-encoded features

        Returns
        -------
        torch.Tensor
            A tensor whose label encoded features have been replaced with a one-hot encoding
        """
        # tensor is of shape (batch size, num features, seq len)
        shape = tensor.shape
        out_features = shape[1] - len(self.cardinality) + sum(self.cardinality)
        out = torch.zeros(shape[0], out_features, shape[2])
        orig_cur_ind = 0
        new_cur_ind = 0

        # fill one hots
        for ind, card in zip(self.feature_indices, self.cardinality):
            if ind > orig_cur_ind:
                num_copied = ind - orig_cur_ind
                out[:, new_cur_ind : new_cur_ind + num_copied, :] = tensor[:, orig_cur_ind:ind, :]
                orig_cur_ind += num_copied
                new_cur_ind += num_copied

            out[:, new_cur_ind : new_cur_ind + card, :] = F.one_hot(tensor[:, ind, :].long(), card).transpose(1, 2)
            orig_cur_ind += 1
            new_cur_ind += card

        # fill after if needed
        if new_cur_ind < out_features:
            out[:, new_cur_ind:, :] = tensor[:, orig_cur_ind:, :]
        return out

    def decode(self, tensor: torch.Tensor) -> torch.Tensor:
        """Reverses a one-hot encoding, converting OHE features to a label-encoding.

        Parameters
        ----------
        tensor: torch.Tensor
            The tensor which contains one or more OHE features

        Returns
        -------
        torch.Tensor
            A tensor whose OHE features have been replaced with a label encoding
        """
        shape = tensor.shape
        out_features = shape[1] - sum(self.cardinality) + len(self.cardinality)
        out = torch.zeros(shape[0], out_features, shape[2])
        orig_cur_ind = 0
        new_cur_ind = 0

        for ind, card in zip(self.feature_indices, self.cardinality):
            if ind > orig_cur_ind:
                num_copied = ind - orig_cur_ind
                out[:, orig_cur_ind:ind, :] = tensor[:, new_cur_ind : new_cur_ind + num_copied, :]
                orig_cur_ind += num_copied
                new_cur_ind += num_copied

            out[:, ind, :] = tensor[:, new_cur_ind : new_cur_ind + card, :].argmax(1).type(tensor.dtype)
            orig_cur_ind += 1
            new_cur_ind += card

        # fill after if needed
        if orig_cur_ind < out_features:
            out[:, orig_cur_ind:, :] = tensor[:, new_cur_ind:, :]
        return out


@dc.dataclass
class BatchOneHotEncoder:
    """Applies one hot encoding to a batch.

    Attributes
    ----------
    past_regressor: OneHotEncoder, optional
        The one hot encoding to apply to past regressors. Defaults to None.
    future_regressor: OneHotEncoder, optional
        The one hot encoding to apply to future regressors. Defaults to None.

    """

    past_regressor: Optional[OneHotEncoder] = None
    future_regressor: Optional[OneHotEncoder] = None

    def __post_init__(self):
        """Validates the batch one-hot encoder."""
        if self.past_regressor is None and self.future_regressor is None:
            raise ValueError("Either past_regressor or future_regressor must not be None.")

    def encode(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Applies the one hot encoding to the batch.

        Parameters
        ----------
        batch: BatchType
            The batch to which the one hot encoding should be applied
        inplace: bool, optional
            Should the batch be modified in place or should a (shallow) copy be modified. Defaults to False.
            Note: If inplace = True, OHE fields will be new tensors whereas unchanged fields will be a reference to the
            original tensor..

        Returns
        -------
        BatchType
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)
        if self.past_regressor and PAST_IND_KEY in out:
            out[PAST_IND_KEY] = self.past_regressor.encode(batch[PAST_IND_KEY])
        if self.future_regressor and FUTURE_IND_KEY in out:
            out[FUTURE_IND_KEY] = self.future_regressor.encode(batch[FUTURE_IND_KEY])
        return out

    def decode(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Inverts the one hot encoding already applied to a given batch.

        Parameters
        ----------
        batch: BatchType
            The batch on which the one hot encoding should be inverted
        inplace: bool, optional
            Should the batch be modified in place or should a (shallow) copy be modified. Defaults to False.
            Note: If inplace = True, OHE fields will be new tensors whereas unchanged fields will be a reference to the
            original tensor.

        Returns
        -------
        None
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)
        if self.past_regressor and PAST_IND_KEY in out:
            out[PAST_IND_KEY] = self.past_regressor.decode(batch[PAST_IND_KEY])
        if self.future_regressor and FUTURE_IND_KEY in out:
            out[FUTURE_IND_KEY] = self.future_regressor.decode(batch[FUTURE_IND_KEY])
        return out
