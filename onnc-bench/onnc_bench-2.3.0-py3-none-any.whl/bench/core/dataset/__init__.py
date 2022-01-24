from enum import Enum

# from .layout import DataLayout
# from .dataset import Dataset
# from .identifier import Identifier
# from .transformer import DatasetTransformer


__DATASET__ = '__DATASET__'


class DatasetFormat(Enum):
    NON_SPECIFIED = 0
    UNKNOWN = 1

    NPY = 11
    NPYDIR = 12
    NPZ = 13
    NDARRAY = 14
    NP_MEMMAP = 15
    NPZ_OBJECT = 16

    PB = 17

    ONNC_DATASET = 51

    TORCH_DATASET = 100
    TORCH_DATALOADER = 101

    KERAS_DATASET = 200
    TFDS_PREFETCH = 201 # tensorflow.python.data.ops.dataset_ops.PrefetchDataset

