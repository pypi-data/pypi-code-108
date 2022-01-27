from typing import Mapping

import torch
from catalyst.core import IRunner
from catalyst.utils import any2device
from torch.utils.data import SequentialSampler


def should_skip_loader(state: IRunner, loaders_to_skip):
    if not isinstance(state.loaders[state.loader_key].sampler, SequentialSampler):
        return True
    if state.loader_key in loaders_to_skip:
        return True
    return False


def batch_to_device(batch, device) -> Mapping[str, torch.Tensor]:
    return any2device(batch, device)