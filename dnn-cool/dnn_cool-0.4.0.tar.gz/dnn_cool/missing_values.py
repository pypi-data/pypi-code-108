import numpy as np
import torch


def positive_values(values):
    if not isinstance(values, torch.Tensor) and not isinstance(values, np.ndarray):
        return [positive_values(v) for v in values]
    tensor: torch.Tensor = values
    mask = tensor >= 0.
    axes = tuple(range(1, len(mask.shape)))
    if len(axes) > 0:
        mask = mask.sum(axis=axes) > 0
    return mask


def all_correct(tensor):
    return torch.ones(len(tensor), dtype=bool)
