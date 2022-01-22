import ctypes
import math
import multiprocessing as mp

import numpy as np

import torch
from torch.utils.data import Dataset


class CachedDataset(Dataset):
    def __init__(self, dataset):
        self.dataset = dataset

        # Use first dataset item as reference
        outputs = self.dataset[0]
        self.output_tuple = isinstance(outputs, tuple)
        if not self.output_tuple:
            outputs = (outputs,)

        self.shared_arrays = []
        length = len(self.dataset)
        for output in outputs:
            if not isinstance(output, torch.Tensor):
                output = torch.as_tensor(output)
            shape = (length,) + output.shape
            shared_array = _create_shared_array(shape, output.dtype)
            self.shared_arrays.append(shared_array)

        self.cached = _create_shared_array((length,), torch.bool)

    def __getitem__(self, index):
        if not self.cached[index]:
            outputs = self.dataset[index]
            if not self.output_tuple:
                outputs = (outputs,)
            for i, output in enumerate(outputs):
                self.shared_arrays[i][index] = output
            self.cached[index] = True

        if self.output_tuple:
            return tuple(array[index] for array in self.shared_arrays)
        return self.shared_arrays[0][index]

    def __len__(self):
        return len(self.dataset)


def _create_shared_array(shape, dtype):
    dtypes = {
        torch.bool: ctypes.c_bool,
        torch.int32: ctypes.c_int32,
        torch.int64: ctypes.c_int64,
        torch.float: ctypes.c_float,
        torch.double: ctypes.c_double,
    }
    shared_array_base = mp.Array(dtypes[dtype], math.prod(shape))
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    return torch.as_tensor(shared_array, dtype=dtype).view(shape)
