"""Stateless, univariate feature transforms."""

import copy
import dataclasses as dc
from typing import Callable, List, Sequence, Union

import torch

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms.common import BatchType, make_int_list


Transform = Callable[[torch.Tensor], torch.Tensor]


def _make_callable_list(c: Union[Transform, Sequence[Transform]]) -> List[Transform]:
    if isinstance(c, Callable):
        return [c]
    else:
        return list(c)


@dc.dataclass
class FeatureTransform:
    """Applies 1+ stateless univariate feature transform(s) to 1+ features in a tensor.

    Attributes
    ----------
    feature_indices: Union[int, Sequence[int]]
        Which features of the tensor should be transformed. All transforms are applied to all feature_indices.
    transforms: Union[Transform, Sequence[Transform]]
        Which transforms should be performed; each transform is a function mapping tensor -> tensor
    inverse_transforms: Union[Transform, Sequence[Transform]]
        The inverse of each of transform listed above in an identical order
    """

    feature_indices: Union[int, Sequence[int]]
    transforms: Union[Transform, Sequence[Transform]]
    inverse_transforms: Union[Transform, Sequence[Transform]]

    def __post_init__(self):
        """Validates the FeatureTransform."""
        self.feature_indices = make_int_list(self.feature_indices)
        self.transforms = _make_callable_list(self.transforms)
        self.inverse_transforms = _make_callable_list(self.inverse_transforms)
        if len(self.transforms) != len(self.inverse_transforms):
            raise ValueError("transforms and inverse_transforms must be of the same length")
        if not self.transforms:
            raise ValueError("Must include at least one transform")

    def apply(self, tensor: torch.Tensor, *, inplace: bool = False) -> torch.Tensor:
        """Applies the transform.

        Parameters
        ----------
        tensor: torch.Tensor
            The tensor to transform
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        torch.Tensor
        """
        if inplace:
            out = tensor
        else:
            out = tensor.detach().clone()
        for tf in self.transforms:
            out[:, self.feature_indices, :] = tf(out[:, self.feature_indices, :])
        return out

    def undo(self, tensor: torch.Tensor, *, inplace: bool = False) -> torch.Tensor:
        """Undoes the transform.

        Parameters
        ----------
        tensor: torch.Tensor
            The tensor to un-transform
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        torch.Tensor
        """
        if inplace:
            out = tensor
        else:
            out = tensor.detach().clone()
        for itf in reversed(self.inverse_transforms):
            out[:, self.feature_indices, :] = itf(out[:, self.feature_indices, :])
        return out


@dc.dataclass
class BatchFeatureTransform:
    """Applies FeatureTransforms to each component of a batch.

    Attributes
    ----------
    past_regressor: Union[FeatureTransform, Sequence[FeatureTransform], None], optional
    past_regressand: Union[FeatureTransform, Sequence[FeatureTransform], None], optional
    future_regressor: Union[FeatureTransform, Sequence[FeatureTransform], None], optional
    future_regressand: Union[FeatureTransform, Sequence[FeatureTransform], None], optional

    Each attribute, which defaults to None, corresponds to 1+ feature transform. While a FeatureTransform may apply 1+
    functions, they are applied to a fixed set of indices. Therefore, a sequence of FeatureTransforms allows for
    different transforms to be applied to different feature_indices. Defaults to None, which corresponds to no
    transform.
    """

    past_regressor: Union[FeatureTransform, Sequence[FeatureTransform], None] = None
    past_regressand: Union[FeatureTransform, Sequence[FeatureTransform], None] = None
    future_regressor: Union[FeatureTransform, Sequence[FeatureTransform], None] = None
    future_regressand: Union[FeatureTransform, Sequence[FeatureTransform], None] = None

    def __post_init__(self):
        """Validate the BatchNormalizer object."""
        if (
            not self.past_regressor
            and not self.past_regressand
            and not self.future_regressor
            and not self.future_regressand
        ):
            raise ValueError("At least one of FeatureTransforms must be set.")

        for field in dc.fields(self):
            f = getattr(self, field.name)
            if isinstance(f, FeatureTransform):
                setattr(self, field.name, [f])
            elif isinstance(f, Sequence):
                setattr(self, field.name, list(f))
            elif f is not None:
                raise ValueError(f"Bad type ({type(f)}) for field {field.name}")

    def apply(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Applies the BatchFeatureTransform to a batch.

        Parameters
        ----------
        batch: BatchType
            The batch to transform
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        BatchType
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self.past_regressor and PAST_IND_KEY in out:
            for tf in self.past_regressor:
                out[PAST_IND_KEY] = tf.apply(out[PAST_IND_KEY], inplace=inplace)
        if self.past_regressand and PAST_DEP_KEY in out:
            for tf in self.past_regressand:
                out[PAST_DEP_KEY] = tf.apply(out[PAST_DEP_KEY], inplace=inplace)
        if self.future_regressor and FUTURE_IND_KEY in out:
            for tf in self.future_regressor:
                out[FUTURE_IND_KEY] = tf.apply(out[FUTURE_IND_KEY], inplace=inplace)
        if self.future_regressand and FUTURE_DEP_KEY in out:
            for tf in self.future_regressand:
                out[FUTURE_DEP_KEY] = tf.apply(out[FUTURE_DEP_KEY], inplace=inplace)
        return out

    def undo(self, batch: BatchType, *, inplace: bool = False) -> BatchType:
        """Undoes a BatchFeatureTransform which was applied to a batch.

        Parameters
        ----------
        batch: BatchType
            The batch to un-transform
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        BatchType
        """
        if inplace:
            out = batch
        else:
            out = copy.copy(batch)

        if self.past_regressor and PAST_IND_KEY in out:
            for tf in reversed(self.past_regressor):
                out[PAST_IND_KEY] = tf.undo(out[PAST_IND_KEY], inplace=inplace)
        if self.past_regressand and PAST_DEP_KEY in out:
            for tf in reversed(self.past_regressand):
                out[PAST_DEP_KEY] = tf.undo(out[PAST_DEP_KEY], inplace=inplace)
        if self.future_regressor and FUTURE_IND_KEY in out:
            for tf in reversed(self.future_regressor):
                out[FUTURE_IND_KEY] = tf.undo(out[FUTURE_IND_KEY], inplace=inplace)
        if self.future_regressand and FUTURE_DEP_KEY in out:
            for tf in reversed(self.future_regressand):
                out[FUTURE_DEP_KEY] = tf.undo(out[FUTURE_DEP_KEY], inplace=inplace)
        return out

    def undo_y(self, y: torch.Tensor, *, inplace: bool = False) -> torch.Tensor:
        """Undoes a transformed target/forecast.

        Parameters
        ----------
        y: torch.Tensor
            The target/forecast to un-transform
        inplace: bool, optional
            Should the operation be performed inplace, defaults to False

        Returns
        -------
        torch.Tensor
        """
        if not self.future_regressand:
            return y

        if inplace:
            out = y
        else:
            out = y.detach().clone()

        for tf in reversed(self.future_regressand):
            out = tf.undo(out, inplace=inplace)
        return out
