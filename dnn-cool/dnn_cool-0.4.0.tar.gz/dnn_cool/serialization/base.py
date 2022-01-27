import joblib
import numpy as np

from dnn_cool.utils.base import squeeze_last_axis_if_needed
from mmap_ninja import numpy


def concat_nested(key, value, precondition_dict):
    valid_values = []
    valid_indices = []
    offset = 0
    for i in range(len(value)):
        arr = value[i]
        preconditions = precondition_dict.get(f'precondition|{key}')
        precondition = preconditions[i] if preconditions is not None else np.ones_like(arr, dtype=bool)
        precondition = squeeze_last_axis_if_needed(precondition)
        valid_values.append(arr[precondition])
        valid_axes = np.where(precondition)
        for axis, nonzero in enumerate(valid_axes):
            if not (axis < len(valid_indices)):
                valid_indices.append([])
            if axis == 0:
                nonzero += offset
                offset += len(arr)
            valid_indices[axis].append(nonzero)
    valid_values = np.concatenate(valid_values, axis=0)
    valid_indices = squeeze_last_axis_if_needed(np.stack([np.concatenate(v) for v in valid_indices]).T)
    return valid_indices, valid_values


def to_dict_of_lists(nested_dict, precondition_dict, parent_dir, name, loader_key, interpretation_mode=False):
    res = {}
    for key, value in nested_dict.items():
        if key.startswith('precondition'):
            continue
        if parent_dir is None:
            continue
        out_dir = parent_dir / loader_key
        out_dir.mkdir(exist_ok=True)
        out_dir = (out_dir / name)
        out_dir.mkdir(exist_ok=True)
        if interpretation_mode:
            res[key] = numpy.from_ndarray(out_dir / key, value)
            continue
        valid_indices, valid_values = concat_nested(key, value, precondition_dict)
        res[key] = valid_values
        values = numpy.from_ndarray(out_dir / key, valid_values)
        indices_dir = (parent_dir / loader_key / 'indices')
        indices_dir.mkdir(exist_ok=True)
        indices = numpy.from_ndarray(parent_dir / loader_key / 'indices' / key, valid_indices)
    return res
