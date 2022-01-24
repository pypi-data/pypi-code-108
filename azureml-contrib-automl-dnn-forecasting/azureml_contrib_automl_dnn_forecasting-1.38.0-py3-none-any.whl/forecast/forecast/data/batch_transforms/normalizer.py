"""Performs feature-wise normalization."""

import copy
import dataclasses as dc
import enum
from typing import Optional, Sequence, Union

import torch

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms.common import BatchType, make_int_list


class NormalizationMode(enum.Enum):
    """Should feature-wise normalization be performed per-series or globally across all series."""

    PER_SERIES = "per_series"
    GLOBAL = "global"


@dc.dataclass
class Normalizer:
    """Performs feature-wise normalization on a subset of a batch.

    Attributes
    ----------
    feature_indices: Union[int, Sequence[int]]
        The indices of the features to be normalized
    offset: torch.Tensor
        The offset to be subtracted from the features. If mode == PER_SERIES, offset should be of shape
        (num_series, num_feature). If mode == GLOBAL, offset should be of shape (num_features,).
    scale: torch.Tensor
        The scale factor to be applied to the offset-subtracted features. If mode == PER_SERIES, scale should be of
        shape (num_series, num_feature). If mode == GLOBAL, scale should be of shape (num_features,).
    mode: NormalizationMode
        Specifies whether the normalization should be per series or global across all series.
    """

    feature_indices: Union[int, Sequence[int]]
    offset: torch.Tensor  # either (num_series, num_feature) or (num_feature,)
    scale: torch.Tensor
    mode: NormalizationMode

    def __post_init__(self):
        """Validates the dataclass object."""
        self.feature_indices = make_int_list(self.feature_indices)

        # check the dims of offset/scale
        if self.offset.shape != self.scale.shape:
            raise ValueError(f"Shape of offset {self.offset.shape} must match that of scale {self.scale.shape}")

        num_features = len(self.feature_indices)
        if num_features != self.offset.shape[-1]:
            raise ValueError(
                f"number of feature indices ({num_features}) must equal that of offset/scale ({self.offset.shape})"
            )

        if self.mode is NormalizationMode.PER_SERIES:
            if self.offset.ndim != 2:
                raise ValueError(
                    "Shape of `offset` must be (n_series, n_features) for per-series normalization; "
                    f"received {self.offset.shape}"
                )
            elif self.scale.ndim != 2:
                raise ValueError(
                    "Shape of `scale` must be (n_series, n_features) for per-series normalization; "
                    f"received {self.scale.shape}"
                )
        elif self.mode is NormalizationMode.GLOBAL:
            if self.offset.ndim != 1:
                raise ValueError(
                    f"Shape of `offset` must be (n_features,) for global normalization; received {self.offset.shape}"
                )
            elif self.offset.ndim != 1:
                raise ValueError(
                    f"Shape of `scale` must be (n_features,) for global normalization; received {self.scale.shape}"
                )

    def normalize(
        self,
        tensor: torch.Tensor,
        series_indices: Optional[torch.LongTensor] = None,
        *,
        inplace: bool = False,
    ) -> torch.Tensor:
        """Performs feature-wise normalization as specified by the dataclass configuration.

        Parameters
        ----------
        tensor: torch.Tensor
            The full tensor to be normalized
        series_indices
            The indices of the series specified in tensor
        inplace: bool, optional
            Perform the normalization inplace, defaults to False.

        Returns
        -------
        torch.Tensor
        """
        if inplace:
            out = tensor
        else:
            out = tensor.detach().clone()

        if self.mode is NormalizationMode.PER_SERIES:
            if series_indices is None:
                raise ValueError("series indices are required for per-series normalization")
            out[:, self.feature_indices, :] -= self.offset[series_indices, :, None]
            out[:, self.feature_indices, :] /= self.scale[series_indices, :, None]
        elif self.mode is NormalizationMode.GLOBAL:
            out[:, self.feature_indices, :] -= self.offset[:, None]
            out[:, self.feature_indices, :] /= self.scale[:, None]
        else:
            raise ValueError(f"Unknown configuration mode: {self.mode}")
        return out

    def denormalize(
        self,
        tensor: torch.Tensor,
        series_indices: Optional[torch.LongTensor] = None,
        *,
        inplace: bool = False,
    ) -> torch.Tensor:
        """Performs feature-wise denormalization as specified by the dataclass configuration.

        Parameters
        ----------
        tensor: torch.Tensor
            The full tensor to be denormalized
        series_indices
            The indices of the series specified in tensor
        inplace: bool, optional
            Perform the denormalization inplace, defaults to False.

        Returns
        -------
        torch.Tensor
        """
        if inplace:
            out = tensor
        else:
            out = tensor.detach().clone()

        if self.mode is NormalizationMode.PER_SERIES:
            if series_indices is None:
                raise ValueError("series indices are required for per-series denormalization")
            out[:, self.feature_indices, :] *= self.scale[series_indices, :, None]
            out[:, self.feature_indices, :] += self.offset[series_indices, :, None]
        elif self.mode is NormalizationMode.GLOBAL:
            out[:, self.feature_indices, :] *= self.scale[:, None]
            out[:, self.feature_indices, :] += self.offset[:, None]
        else:
            raise ValueError(f"Unknown configuration mode: {self.mode}")
        return out


@dc.dataclass
class BatchNormalizer:
    """Performs feature-wise normalization on a batch of data."""

    past_regressor: Optional[Normalizer] = None
    past_regressand: Optional[Normalizer] = None
    future_regressor: Optional[Normalizer] = None
    future_regressand: Optional[Normalizer] = None

    def __post_init__(self):
        """Validate the BatchNormalizer object."""
        if (
            self.past_regressor is None
            and self.past_regressand is None
            and self.future_regressor is None
            and self.future_regressand is None
        ):
            raise ValueError("At least one of Normalizers must be set.")

        if (
            getattr(self.past_regressor, "mode", None) is NormalizationMode.PER_SERIES
            or getattr(self.past_regressand, "mode", None) is NormalizationMode.PER_SERIES
            or getattr(self.future_regressor, "mode", None) is NormalizationMode.PER_SERIES
            or getattr(self.future_regressand, "mode", None) is NormalizationMode.PER_SERIES
        ):
            self._requires_series_ids = True
        else:
            self._requires_series_ids = False

    def normalize(
        self, batch: BatchType, series_indices: Optional[torch.LongTensor] = None, *, inplace: bool = False
    ) -> BatchType:
        """Performs feature-wise normalization of a batch.

        Parameters
        ----------
        batch: BatchType
            The batch of data to normalize
        series_indices: torch.LongTensor, optional
            The series index of each element in the batch. Required for per-series normalization, otherwise ignored.
            Defaults to None.
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        BatchType
        """
        if self._requires_series_ids and series_indices is None:
            raise ValueError("`series_indices` must be included to perform per-series normalization.")

        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self.past_regressor and PAST_IND_KEY in batch:
            out[PAST_IND_KEY] = self.past_regressor.normalize(batch[PAST_IND_KEY], series_indices, inplace=inplace)
        if self.past_regressand and PAST_DEP_KEY in batch:
            out[PAST_DEP_KEY] = self.past_regressand.normalize(batch[PAST_DEP_KEY], series_indices, inplace=inplace)
        if self.future_regressor and FUTURE_IND_KEY in batch:
            out[FUTURE_IND_KEY] = self.future_regressor.normalize(
                batch[FUTURE_IND_KEY], series_indices, inplace=inplace
            )
        if self.future_regressand and FUTURE_DEP_KEY in batch:
            out[FUTURE_DEP_KEY] = self.future_regressand.normalize(
                batch[FUTURE_DEP_KEY], series_indices, inplace=inplace
            )
        return out

    def denormalize(
        self,
        batch: BatchType,
        series_indices: Optional[torch.LongTensor] = None,
        *,
        inplace: bool = False,
    ) -> BatchType:
        """Undoes feature-wise normalization of a batch.

        Parameters
        ----------
        batch: BatchType
            The batch of data to denormalize
        series_indices: torch.LongTensor, optional
            The series index of each element in the batch. Required for per-series denormalization, otherwise ignored.
            Defaults to None.
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        BatchType
        """
        if self._requires_series_ids and series_indices is None:
            raise ValueError("`series_indices` must be included to denormalize per-series normalization.")

        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self.past_regressor and PAST_IND_KEY in batch:
            out[PAST_IND_KEY] = self.past_regressor.denormalize(batch[PAST_IND_KEY], series_indices, inplace=inplace)
        if self.past_regressand and PAST_DEP_KEY in batch:
            out[PAST_DEP_KEY] = self.past_regressand.denormalize(batch[PAST_DEP_KEY], series_indices, inplace=inplace)
        if self.future_regressor and FUTURE_IND_KEY in batch:
            out[FUTURE_IND_KEY] = self.future_regressor.denormalize(
                batch[FUTURE_IND_KEY], series_indices, inplace=inplace
            )
        if self.future_regressand and FUTURE_DEP_KEY in batch:
            out[FUTURE_DEP_KEY] = self.future_regressand.denormalize(
                batch[FUTURE_DEP_KEY], series_indices, inplace=inplace
            )

        return out

    def denormalize_prediction(
        self, y: torch.Tensor, series_indices: Optional[torch.LongTensor] = None, *, inplace: bool = False
    ) -> torch.Tensor:
        """Undoes feature-wise normalization of a target/forecast.

        Parameters
        ----------
        y: torch.Tensor
            The target / forecast to denormalize
        series_indices: torch.LongTensor, optional
            The series index of each element in the batch. Required for per-series denormalization, otherwise ignored.
            Defaults to None.
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        torch.Tensor
        """
        if self.future_regressand is None:
            return y
        if self.future_regressand.mode is NormalizationMode.PER_SERIES and series_indices is None:
            raise ValueError("`series_indices` must be included to denormalize per-series normalization.")
        return self.future_regressand.denormalize(y, series_indices, inplace=inplace)
