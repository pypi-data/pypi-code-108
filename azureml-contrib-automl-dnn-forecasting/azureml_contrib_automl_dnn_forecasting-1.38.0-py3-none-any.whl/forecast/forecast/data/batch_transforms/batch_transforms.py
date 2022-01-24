"""Batch Transforms operate on a full batch of tensor data.

To increase prediction efficiency, batch transforms operate on a full batch of tensor data rather than on individual
samples. This obviates the need for splitting, individually transforming, and aggregating samples from a batched
prediction.
"""

import abc
import copy
from typing import Callable, Optional

import torch

from forecast.data import PAST_IND_KEY
from forecast.data.batch_transforms.common import BatchType
from forecast.data.batch_transforms.feature_transform import BatchFeatureTransform
from forecast.data.batch_transforms.normalizer import BatchNormalizer
from forecast.data.batch_transforms.one_hot import BatchOneHotEncoder
from forecast.data.batch_transforms.subtract_offset import BatchSubtractOffset


class BatchTransform(abc.ABC):
    """A transformer for a batch of data samples.

    This transform:
    - transforms a batch of data before it is supplied to a model for training/inference
    - inverts the transform to retrieve

    Batches
    """

    @abc.abstractmethod
    def do(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Transforms a batch.

        Parameters
        ----------
        batch: BatchType
            A batch of data
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        BatchType
            The transformed batch.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def undo_y(self, y: torch.Tensor, batch: BatchType, *, inplace: bool = False) -> torch.Tensor:
        """Reverse the transform for y.

        Parameters:
        -----------
        y: torch.Tensor
            A y tensor. (For example, this tensor could be a tensor of output predictions from the DNN.)
        batch: BatchType
            A batch of data
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        torch.Tensor
            A y tensor with the transform undone.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def undo(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Reverse the transform applied to a batch.

        Parameters
        -----------
        batch: BatchType
            A batch of data
        inplace: bool, optional
            Should the operation be performed inplace

        Returns
        --------
        BatchType
            A batch with the transforms undone
        """
        raise NotImplementedError


class GenericBatchTransform(BatchTransform):
    """A flexible, customizable batch transform designed for reuse."""

    def __init__(
        self,
        feature_transforms: Optional[BatchFeatureTransform] = None,
        normalizer: Optional[BatchNormalizer] = None,
        subtract_offset: Optional[BatchSubtractOffset] = None,
        one_hot: Optional[BatchOneHotEncoder] = None,
        series_indexer: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
    ):
        """Creates the GenericBatchTransform.

        Parameters
        ----------
        feature_transforms: BatchFeatureTransform, optional
            If included, the univariate transforms to be applied to each feature. Defaults to None (no feature
            transformation)
        normalizer: BatchNormalizer, optional
            If included, the feature normalization defined by BatchNormalizer will be performed. Defaults to None (no
            feature normalization)
        subtract_offset: BatchSubtractOffset
            If included, subtracts the last historical value of the regressand from the historical and future values.
        one_hot: BatchOneHotEncoder, optional
            If included, transforms the requested indices into a one hot encoding. Defaults to None (no encoding)
        series_indexer: Callable[[torch.Tensor], torch.LongTensor], optional
            Maps the past regressor to a series index. Needed for any per-series transformations. Defaults to None

        """
        super().__init__()
        self._feature_transformer = feature_transforms
        self._normalizer = normalizer
        self._subtract_offset = subtract_offset
        self._one_hot_encoder = one_hot
        self._series_indexer = series_indexer

    def do(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Transforms a batch.

        Parameters:
        -----------
        batch: BatchType
            A batch of data

        Returns:
        --------
        BatchType
            The transformed batch.
        """
        # compute the series indices if the indexer is present
        series_indices = self._get_series_ids(batch[PAST_IND_KEY])
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self._feature_transformer:
            out = self._feature_transformer.apply(out, inplace=inplace)
        if self._normalizer:
            out = self._normalizer.normalize(out, series_indices, inplace=inplace)
        if self._subtract_offset:
            out = self._subtract_offset.do(out, inplace=inplace)

        # one hot must come last to avoid messing with feature indices used previously
        if self._one_hot_encoder:
            out = self._one_hot_encoder.encode(out, inplace=inplace)

        return out

    def undo_y(self, y: torch.Tensor, batch: BatchType, *, inplace: bool = False) -> torch.Tensor:
        """Reverses the transform for a target / forecast.

        Parameters:
        -----------
        y: torch.Tensor
            A target / forecast which should be un-transformed.
        batch: BatchType
            A batch of data (will not be modified but may be used to invert the transform)
        inplace; bool, optional
            Should the operation be performed inplace, defaults to False

        Returns:
        --------
        torch.Tensor
            A target/forecast with the transform undone.
        """
        # Todo: only proceed if y is modified
        series_indices = self._get_series_ids(batch[PAST_IND_KEY])
        if inplace:
            out = y
        else:
            out = y.detach().clone()

        # we can skip OHE as it only impacts the regressors and none of the transforms currently depend on their values
        # force inplace to true as we already copied it if needed
        if self._subtract_offset:
            out = self._subtract_offset.undo_y(out, batch, inplace=True)
        if self._normalizer:
            out = self._normalizer.denormalize_prediction(out, series_indices, inplace=True)
        if self._feature_transformer:
            out = self._feature_transformer.undo_y(out, inplace=True)
        return out

    def undo(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Reverse the transform applied to a batch.

        Parameters:
        -----------
        batch: BatchType
            A batch of data
        inplace: bool, optional
            Should the operation be performed inplace

        Returns:
        --------
        torch.Tensor
            A y tensor with the transform undone.
        """
        series_indices = self._get_series_ids(batch[PAST_IND_KEY])
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self._one_hot_encoder:
            out = self._one_hot_encoder.decode(out, inplace=inplace)
        if self._subtract_offset:
            out = self._subtract_offset.undo(out, inplace=inplace)
        if self._normalizer:
            out = self._normalizer.denormalize(out, series_indices, inplace=inplace)
        if self._feature_transformer:
            out = self._feature_transformer.undo(out, inplace=inplace)
        return out

    def _get_series_ids(self, past_regressor: torch.Tensor) -> Optional[torch.LongTensor]:
        return self._series_indexer(past_regressor).long() if self._series_indexer is not None else None
