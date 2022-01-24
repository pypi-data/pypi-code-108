"""A library of data transforms which may be useful in pre-processing data prior to training/inference."""

import abc
import importlib
from types import ModuleType
from typing import Callable, cast, Dict, List, Mapping, Optional, Sequence, Union
import uuid

import numpy as np
import torch
from typing_extensions import TypedDict

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY


TSampleVal = Union[np.ndarray, torch.Tensor]
TSample = Dict[str, TSampleVal]


def _get_mod(x: TSampleVal) -> ModuleType:
    """Returns the module of the input type x."""
    if isinstance(x, np.ndarray):
        return np
    elif isinstance(x, torch.Tensor):
        return torch
    else:
        raise ValueError('`x` must be of type `numpy.ndarray` or `torch.Tensor`')


def _copy(x: TSampleVal) -> TSampleVal:
    if isinstance(x, np.ndarray):
        return x.copy()
    elif isinstance(x, torch.Tensor):
        return x.clone().detach()
    else:
        raise ValueError(f'Unknown type {x}')


def _copy_for_inplace(sample: TSample, keys: Sequence[str], inplace: bool) -> TSample:
    if not inplace:
        sample = {k: _copy(v) if k in keys else v for k, v in sample.items()}
    return sample


class AbstractTransform(abc.ABC):
    """Defines the API (do and undo) from which all transforms are derived."""

    @abc.abstractmethod
    def do(self, sample: TSample) -> TSample:
        """Performs the transform.

        Parameters
        ----------
        sample: dict[str] -> np.ndarray or torch.Tensor
            The input to be transformed

        Returns
        -------
        dict[str] -> np.ndarray or torch.Tensor
            The transformed inputs

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def undo(self, sample: TSample) -> TSample:
        """Undoes the previously performed transform.

        Parameters
        ----------
        sample: dict[str] -> np.ndarray or torch.Tensor
            A previously transformed sample

        Returns
        -------
        dict[str] -> np.ndarray, torch.Tensor
            The input previously passed to the transform

        """
        raise NotImplementedError()

    def __call__(self, sample: TSample) -> TSample:
        """Shorthand for invoking the `do` method.

        Parameters
        ----------
        sample: dict[str] -> np.ndarray or torch.Tensor
            The input to be transformed

        Returns
        -------
        dict[str] -> np.ndarray or torch.Tensor
            The transformed inputs

        """
        return self.do(sample)


class LogTransform(AbstractTransform):
    """Natural logarithm of target + `offset`."""

    def __init__(self, offset: float = 0.0, targets: Optional[Union[int, Sequence[int]]] = None, inplace: bool = False):
        """Computes the natural logarithm of the sample's target after applying an optional offset.

        Parameters
        ----------
        offset: float
            An offset to apply to the targets before computing the natural logarithm
        targets: int, List[int]
            One or more indices of rows on which the transform should be applied
        inplace: bool, optional
            Perform the transform inplace rather than generating a copy

        """
        super().__init__()
        self.offset = offset
        self.targets = targets
        self._inplace = inplace
        self._keys = [PAST_DEP_KEY, FUTURE_DEP_KEY]

    def do(self, sample: TSample) -> TSample:
        """Computes the natural logarithm of the sample's target after applying an optional offset.

        Parameters
        ----------
        sample: TSample
            The sample whose target indices will be transformed by a natural logarithm

        Returns
        -------
        TSample
            The transformed sample

        """
        sample = _copy_for_inplace(sample, self._keys, self._inplace)
        for key in self._keys:
            x = sample[key]
            mod = _get_mod(x)

            if self.targets:
                x[self.targets, :] = mod.log(self.offset + x[self.targets, :])
            else:
                x = mod.log(self.offset + x)  # type: ignore

            sample[key] = x

        return sample

    def undo(self, sample: TSample) -> TSample:
        """Undoes a previously applied natural logarithm on the sample's target.

        Parameters
        ----------
        sample: TSample
            The sample whose target indices have been transformed by a natural logarithm

        Returns
        -------
        TSample
            The untransformed sample

        """
        sample = _copy_for_inplace(sample, self._keys, self._inplace)

        for key in self._keys:
            x = sample[key]
            mod = _get_mod(x)

            if self.targets:
                x[self.targets, :] = mod.exp(x[self.targets, :]) - self.offset
            else:
                x = mod.exp(x) - self.offset  # type: ignore

            sample[key] = x

        return sample


class SubtractOffset(AbstractTransform):
    """For target rows, subtract value at temporal index from time series."""

    def __init__(self, index: Optional[int] = -1, targets: Optional[Union[int, Sequence[int]]] = None):
        """For target rows, subtract value at temporal index from time series.

        Parameters
        ----------
        index: int, optional
            The sample index from which the target channels should be transformed (defaults to -1, the last sample).

        targets: int | List[int], optional
            The target channels on which the subtraction should be performed.

        """
        super().__init__()
        self.index = index
        self.targets = targets
        self._uuid = uuid.uuid4()

    def do(self, sample: TSample) -> TSample:
        """For target rows, subtract value at temporal index from time series.

        Parameters
        ----------
        sample: TSample
            The sample which should be transformed

        Returns
        -------
        TSample
            The transformed sample

        """
        output = dict(sample)

        # get offset for selected targets
        if self.targets:
            offset = sample[PAST_DEP_KEY][self.targets, self.index]
        else:
            offset = sample[PAST_DEP_KEY][:, self.index]

        # subtract offset from targets
        for key in [PAST_DEP_KEY, FUTURE_DEP_KEY]:
            x = _copy(sample[key])
            if self.targets:
                x[self.targets, :] = x[self.targets, :] - offset[:, None]
            else:
                x = x - offset[:, None]
            output[key] = x

        # persist offset so that we may undo the subtraction later
        output[f'_{self._uuid}_offset'] = offset
        return output

    def undo(self, sample: TSample) -> TSample:
        """For target rows, adds back the offset which was previously subtracted.

        Parameters
        ----------
        sample: TSample
            The sample which previously had been transformed

        Returns
        -------
        TSample
            The original, un-transformed sample

        """
        output = dict(sample)
        offset = output[f'_{self._uuid}_offset']

        if isinstance(sample[PAST_DEP_KEY], np.ndarray) and isinstance(offset, torch.Tensor):
            offset = offset.detach().to('cpu').numpy()

        for key in [PAST_DEP_KEY, FUTURE_DEP_KEY]:
            x = _copy(sample[key])
            if self.targets:
                x[self.targets, :] = x[self.targets, :] + offset[:, None]
            else:
                x += offset[:, None]
            output[key] = x

        return output


class ToTensor(AbstractTransform):
    """Ensures the X, y elements of the sample are on the correct device with the correct type."""

    def __init__(self, device: str = 'cpu'):
        """Ensures the X, y elements of the sample are on the correct device with the correct type.

        Parameters
        ----------
        device: str
            The device on which the tensor should be located

        """
        super().__init__()
        self.device = torch.device(device)
        self._uuid = uuid.uuid4()
        self.fields = [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY, FUTURE_DEP_KEY]

    def do(self, sample: TSample) -> TSample:
        """Ensures the X, y elements of the sample are on the correct device with the correct type.

        Parameters
        ----------
        sample: TSample
            The sample to potentially convert and move

        Returns
        -------
        TSample
            The sample whose X, y elements are on the specified devices

        """
        output = dict(sample)
        for field in self.fields:
            val = output[field]
            t = type(val)
            output[f'_{self._uuid}_orig_{field}_type_module'] = t.__module__
            output[f'_{self._uuid}_orig_{field}_type_class'] = t.__qualname__
            output[f'_{self._uuid}_orig_{field}_device'] = str(val.device) if isinstance(val, torch.Tensor) else 'cpu'

            # Note: torch will COPY data by default when converting a numpy array to a tensor AND when moving a tensor
            # across devices. Therefore, we do not need to worry about mutating the data.
            if isinstance(val, torch.Tensor):
                # this is a no-op if the device is already correctly set
                output[field] = val.to(self.device)
            elif isinstance(val, np.ndarray):
                output[field] = torch.tensor(val, device=self.device)
            else:
                raise TypeError(f'Unknown type {t}')

        return output

    def undo(self, sample: TSample) -> TSample:
        """Converts the X, y elements of a dict to their original type/device.

        Parameters
        ----------
        sample: TSample
            The sample to revert to its original form

        Returns
        -------
        TSample
            A sample whose X, y elements have been reverted to their original form

        """
        output = dict(sample)

        def convert(var: TSampleVal, module: str, class_name: str, device: str) -> TSampleVal:
            # TODO: this do not convert back to the original subtype; either fix or explicitly document.
            type_ = getattr(importlib.import_module(module), class_name)
            if not isinstance(var, type_):
                if issubclass(type_, np.ndarray):
                    var = var.to('cpu').detach().numpy()
                elif issubclass(type_, torch.Tensor):
                    var = torch.tensor(var, device=device)
                else:
                    raise ValueError('Unknown type')
            elif isinstance(var, torch.Tensor) and var.device != device:
                var = var.to(device)
            return var

        for field in self.fields:
            val = output[field]
            assert isinstance(val, torch.Tensor)

            module = output[f'_{self._uuid}_orig_{field}_type_module']
            class_name = output[f'_{self._uuid}_orig_{field}_type_class']
            dev = output[f'_{self._uuid}_orig_{field}_device']
            output[field] = convert(val, module, class_name, dev)

        return output


class ToFloat(AbstractTransform):
    """Casts a datatype as a float."""

    def __init__(self) -> None:
        """Casts a datatype as a float."""
        self._uuid = uuid.uuid4()
        self.fields = [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY, FUTURE_DEP_KEY]

    def do(self, sample: TSample) -> TSample:
        """Converts the fields to have data of type float.

        Parameters
        ----------
        sample: TSample
            The sample to convert to float

        Returns
        -------
        TSample
            The converted sample

        """
        output = dict(sample)
        for field in self.fields:
            output[f'_{self._uuid}_{field}_dtype'] = output[field].dtype
            if isinstance(output[field], torch.Tensor):
                output[field] = output[field].float()
            elif isinstance(output[field], np.ndarray):
                output[field] = output[field].astype(np.float)
            else:
                raise TypeError(f'Cannot convert type {type(output[field])} to float')
        return output

    def undo(self, sample: TSample) -> TSample:
        """Undoes a previous conversion to type float.

        Parameters
        ----------
        sample: TSample
            The previously converted sample

        Returns
        -------
        TSample
            The sample in its original form

        """
        output = dict(sample)
        for field in self.fields:
            dtype = cast(torch.dtype, output[f'_{self._uuid}_{field}_dtype'])
            if isinstance(output[field], torch.Tensor):
                output[field] = torch.tensor(output[field], dtype=dtype)
            elif isinstance(output[field], np.ndarray):
                output[field] = np.array(output[field], dtype=dtype)
            else:
                raise TypeError(f'Cannot convert type float to {type(output[field])}')
        return output


class OneHotEncode(AbstractTransform):
    """Converts an index into a one-hot encoded vector."""

    def __init__(self,
                 feature_index: Union[int, Sequence[int]],
                 num_values: Union[int, Sequence[int]],
                 drop_first: bool = False,
                 key: str = PAST_IND_KEY):
        """Creates a streaming featurizer which one-hot encodes an index feature.

        Parameters:
        -----------
        feature_index: Union[int, Sequence[int]]
            Row index or indices in the sample corresponding to index features to be one-hot encoded
        num_values: Union[int, Sequence[int]]
            Number of values for each feature to be one-hot encoded (length must match `feature_index`)
        drop_first: bool, optional
            Determines whether index 0 should be mapped to a `num_value` length vector (`drop_first = False`) or a
            `num_value - 1` length vector (`drop_first = True`) where the 0-index is mapped to a vector of 0s. Default
            is `drop_first = False`).
        key: str, optional
            The key of the N-d feature vector in the `dict` passed to `do` and `undo`

        """
        self._encodings = {}
        if isinstance(feature_index, int) and isinstance(num_values, int):
            self._encodings[feature_index] = num_values
        elif isinstance(feature_index, Sequence) and isinstance(num_values, Sequence):
            if len(feature_index) != len(num_values):
                raise ValueError(f'{len(feature_index)} indices were provided, but {len(num_values)} dimensions '
                                 'were provided.')
            elif len(feature_index) != len(set(feature_index)):
                raise ValueError('The elements of `feature_index` are not unique.')

            # NOTE: we assume our dict is ordered. This is true for python3.7+
            sorted_tuples = sorted(zip(feature_index, num_values))
            for k, v in sorted_tuples:
                self._encodings[k] = v
        else:
            raise ValueError(f'Incompatible types for feature_index ({type(feature_index)}) and num_values '
                             f'({type(num_values)})')

        self._drop_first = drop_first
        self._key = key

    def do(self, sample: TSample) -> TSample:
        """Converts feature_index variables in sample to one-hot encodings, preserving the order of features."""
        output = dict(sample)
        feat_vec = sample[self._key]
        t_len = feat_vec.shape[1]
        is_numpy = True if isinstance(feat_vec, np.ndarray) else False

        # TODO: preallocate entire output at start and inserting rather than creating and concating at end
        next_ind = 0
        to_concat = []
        for ind, num_vals in self._encodings.items():
            # compute one-hot representation for our indexed feature
            if is_numpy:
                temp = np.zeros((num_vals, t_len), dtype=feat_vec.dtype)
                temp[feat_vec[ind, :].astype(np.int), np.arange(t_len)] = 1
            else:
                temp = torch.zeros((num_vals, t_len), dtype=feat_vec.dtype)
                temp[feat_vec[ind, :].type(torch.long), torch.arange(t_len)] = 1

            # if drop first, slice out the first feature_index (all 0's indicate feature_index 0)
            if self._drop_first:
                temp = temp[1:, :]

            # if we skipped over one or more indices, insert those before our encoding
            if next_ind < ind:
                to_concat.append(feat_vec[next_ind:ind, :])
            next_ind = ind + 1

            # add our encoding
            to_concat.append(temp)

        # append any remaining features at the end
        if next_ind < feat_vec.shape[0]:
            to_concat.append(feat_vec[next_ind:, :])

        # concatenate our list of such that relative ordering of features is preserved
        if is_numpy:
            out = np.concatenate(to_concat, axis=0)
        else:
            out = torch.cat(to_concat, dim=0).type(feat_vec.dtype)

        # set output (and verify its shape)
        drop = 1 if self._drop_first else 0
        assert out.shape[0] == feat_vec.shape[0] + sum(self._encodings.values()) - (drop + 1) * len(self._encodings)
        output[self._key] = out
        return output

    def undo(self, sample: TSample) -> TSample:
        """Converts one-hot encodings in sample to indices, preserving the order of features."""
        output = dict(sample)
        feat_vec = sample[self._key]
        is_numpy = True if isinstance(feat_vec, np.ndarray) else False
        drop = 1 if self._drop_first else 0

        next_ind = 0
        embed_extra = 0
        to_concat = []
        for ind, num_vals in self._encodings.items():
            assert next_ind <= ind + embed_extra

            # extract the next N non-embedding features
            if next_ind < ind + embed_extra:
                to_concat.append(feat_vec[next_ind:ind+embed_extra, :])

            # extract the next embedding
            embeds = feat_vec[ind + embed_extra:ind + embed_extra + num_vals - drop, :]
            if is_numpy:
                # convert one-hot encoding to index in numpy
                temp = np.argmax(embeds, axis=0).astype(feat_vec.dtype)

                if self._drop_first:
                    # numpy argmax returns the FIRST element with the largest value
                    # Case 1: argmax of N with corresponding max of 1 --> true index of N+1
                    # Case 2: argmax of 0 with corresponding max of 0 --> true index of 0
                    # The max value (at the argmax loc) will either shift by 1 (if the true index is N+1) or do nothing
                    # if the true index is 0
                    temp += np.max(embeds, axis=0)
            else:
                # pytorch argmax provides no guarantees on which element is returned first in the case of ties
                temp = embeds.argmax(dim=0).type(feat_vec.dtype)

                if self._drop_first:
                    # we leverage the fact that the sum of a true index = 0 entry will be 0. in this case, the product
                    # will evaluate to 0. for all other indices, the sum will evaluate to 1 resulting in an increment
                    # of the index.
                    temp = embeds.sum(dim=0) * (temp + 1)

            # expand from 1d to 2d array/tensor
            to_concat.append(temp[None, :])

            # our next non-embedding feature is
            next_ind = ind + embed_extra + num_vals - drop
            embed_extra += num_vals - drop - 1

        # append any remaining features at the end
        if next_ind < feat_vec.shape[0]:
            to_concat.append(feat_vec[next_ind:, :])

        # concatenate our list of such that relative ordering of features is preserved
        if is_numpy:
            out = np.concatenate(to_concat, axis=0)
        else:
            out = torch.cat(to_concat, dim=0)

        # set output (and verify its shape)
        assert out.shape[0] + sum(self._encodings.values()) - (drop + 1) * len(self._encodings) == feat_vec.shape[0]
        output[self._key] = out
        return output


class ComposedTransform(AbstractTransform):
    """Converts a list of transforms into a single transform."""

    def __init__(self, transforms: Sequence[AbstractTransform]):
        """Converts a list of transforms into a single transform.

        Parameters:
        ----------
        transforms: List[AbstractTransform]
            The list of transforms to be converted into a single transform

        """
        super().__init__()
        self.transforms = list(transforms)

    def do(self, sample: TSample) -> TSample:
        """Applies the list of previously specified transforms.

        Parameters
        ----------
        sample: TSample
            The sample to be transformed

        Returns
        -------
        TSample
            The transformed sample

        """
        for tf in self.transforms:
            sample = tf(sample)
        return sample

    def undo(self, sample: TSample) -> TSample:
        """Undoes the list of previously applied transforms by applying their undo in reverse order.

        Parameters
        ----------
        sample: TSample
            The sample which had previously been transformed

        Returns
        -------
        TSample
            The original, un-transformed sample

        """
        for tf in self.transforms[::-1]:
            sample = tf.undo(sample)
        return sample


def unbatch_and_undo(batch: Mapping[str, torch.Tensor],
                     tf: Optional[AbstractTransform],
                     prediction: Optional[torch.Tensor] = None) -> List[dict]:
    """Converts a batch (dict of Tensors) into a dict of lists and applies undo to each.

    Parameters
    ----------
    batch: dict
        A batch created by a PyTorch DataLoader of one or more transformed sample.
    tf: AbstractTransform
        The transform which was applied to the samples
    prediction: torch.Tensor, optional
        The values predicted by a model

    Returns
    -------
    List
        A list of samples whose key

    """
    # if predictions, replace FUTURE_DEP_KEY's entry with the prediction so it receives the same undo treatment
    if prediction is not None:
        batch = {**batch, **{FUTURE_DEP_KEY: prediction}}

    # convert the dict[key, Tensor] --> dict[key, List[Tensor]]
    unbatched = {k: torch.unbind(v) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}

    # assert all lists have the same length
    batch_size = len(next(iter(unbatched.values())))
    assert all(len(l_) == batch_size for l_ in unbatched.values())

    # convert dict[key, List[Tensor]] --> List[dict[key, Tensor]] and apply undo
    if tf:
        return [tf.undo({k: v[i] for k, v in unbatched.items()}) for i in range(batch_size)]
    else:
        return [{k: v[i] for k, v in unbatched.items()} for i in range(batch_size)]


class NormalizingDict(TypedDict):
    offset: np.ndarray
    scale: np.ndarray


class FeatureNormalizer(AbstractTransform):
    def __init__(
        self,
        keys: Union[str, Sequence[str]],
        indices: Union[int, Sequence[int]],
        props: NormalizingDict,
        inplace: bool = False,
    ):
        self._keys = [keys] if isinstance(keys, str) else list(keys)  # listify
        self._indices = [indices] if isinstance(indices, int) else list(indices)
        self._props = props
        self._inplace = inplace

    def do(self, sample: TSample) -> TSample:
        sample = _copy_for_inplace(sample, self._keys, self._inplace)
        for key in self._keys:
            sample[key][self._indices, :] -= _expand_dims(self._props["offset"], -1)
            sample[key][self._indices, :] /= _expand_dims(self._props["scale"], -1)
        return sample

    def undo(self, sample: TSample) -> TSample:
        sample = _copy_for_inplace(sample, self._keys, self._inplace)
        for key in self._keys:
            sample[key][self._indices, :] *= _expand_dims(self._props["scale"], -1)
            sample[key][self._indices, :] += _expand_dims(self._props["offset"], -1)
        return sample


class SeriesFeatureNormalizer(AbstractTransform):
    def __init__(
        self,
        keys: Union[str, Sequence[str]],
        id_index: Union[int, Callable[[np.ndarray], int]],
        indices: Union[int, Sequence[int]],
        props: NormalizingDict,
        inplace: bool = False,
    ):
        self._keys = [keys] if isinstance(keys, str) else list(keys)  # listify
        self._indices = [indices] if isinstance(indices, int) else list(indices)
        self._props = props
        self._inplace = inplace

        if isinstance(id_index, int):
            self._id_indexer = lambda x: x[id_index, 0]
        else:
            self._id_indexer = lambda x: id_index(x[:, 0])

    def do(self, sample: TSample) -> TSample:
        sample = _copy_for_inplace(sample, self._keys, self._inplace)
        id_ = self._id_indexer(sample[PAST_IND_KEY])
        for key in self._keys:
            sample[key][self._indices, :] -= _expand_dims(self._props["offset"][id_, :], -1)
            sample[key][self._indices, :] /= _expand_dims(self._props["scale"][id_, :], -1)
        return sample

    def undo(self, sample: TSample) -> TSample:
        sample = _copy_for_inplace(sample, self._keys, self._inplace)
        id_ = self._id_indexer(sample[PAST_IND_KEY])
        for key in self._keys:
            sample[key][self._indices, :] *= _expand_dims(self._props["scale"][id_, :], -1)
            sample[key][self._indices, :] += _expand_dims(self._props["offset"][id_, :], -1)
        return sample


def _expand_dims(value: TSampleVal, dim):
    if isinstance(value, torch.Tensor):
        return value.unsqueeze(dim)
    elif isinstance(value, np.ndarray):
        return np.expand_dims(value, dim)
    else:
        raise ValueError(f"Unknown value type {type(value)}")
