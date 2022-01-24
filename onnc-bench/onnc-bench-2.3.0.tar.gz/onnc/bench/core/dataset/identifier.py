from __future__ import annotations
import os
import zipfile
from typing import List
from pathlib import Path

import numpy as np
import onnx
from loguru import logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dataset import Dataset

from .dataset import DatasetFormat


class IdentifierRegistry(type):

    REGISTRY: List = []

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY.append(new_cls)
        return new_cls


class Identifier(metaclass=IdentifierRegistry):

    FORMAT: DatasetFormat = DatasetFormat.NON_SPECIFIED

    @classmethod
    def is_me(self, dataset: Dataset) -> bool:
        pass


def identifier_selector(dataset: Dataset) -> Identifier:
    print(Identifier.REGISTRY)
    for identifier in Identifier.REGISTRY:
        if identifier.is_me(dataset):
            return identifier

    raise NotImplementedError(f"Unalble to identify {dataset.src}")


def identify(dataset: Dataset) -> Dataset:
    for identifier in Identifier.REGISTRY:
        if identifier.is_me(dataset):
            return identifier.FORMAT

    raise NotImplementedError(f"Unalble to identify {dataset.src}")


class PB(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.PB

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        path = dataset.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        if str(path).lower().endswith('.pb'):
            return True

        try:
            tensor = onnx.TensorProto()
            with open(dataset.src, 'rb') as f:
                tensor.ParseFromString(f.read())
            dims = list(tensor.dims)
        except:
            return False

        return True if dims else False


class NPY(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NPY

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        path = dataset.src

        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False

        if str(path).lower().endswith('.npy'):
            return True

        with open(path, 'rb') as f:
            return f.read(6) == bytes.fromhex('934E554D5059')


class NPYDIR(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NPYDIR

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        path = dataset.src

        if not (isinstance(path, Path) and path.exists() and path.is_dir()):
            return False

        files = os.listdir(path)
        if not files:
            return False
        return str(files[0]).lower().endswith('.npy')


class NPZ(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NPZ

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        path = dataset.src
        if not (isinstance(path, Path) and path.exists() and path.is_file()):
            return False
        if str(path).lower().endswith('.npy'):
            return True

        try:
            with zipfile.ZipFile(str(path)) as archive:
                for name in archive.namelist():
                    if not name.endswith('.npy'):
                        continue

                    npy = archive.open(name)
                    version = np.lib.format.read_magic(npy)
                    return True
        except Exception as e:
            logger.debug(str(e))

        return False


class NP_ndarray(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NDARRAY

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        return type(dataset.src) is np.ndarray


class NP_memmap(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NP_MEMMAP

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        return type(dataset.src) is np.memmap


class NPZFileObject(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.NPZ_OBJECT

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        return dataset.src.__class__.__name__ == "NpzFile"


class TorchDatasetObject(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.TORCH_DATASET

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        # from torch.utils.data.dataset import Dataset as TorchDataset
        # return isinstance(dataset.src, TorchDataset)
        str_type = str(dataset.src.__class__.__mro__)
        return '.Dataset' in str_type and 'torch.' in str_type


class TorchDataloaderObject(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.TORCH_DATALOADER

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        # from torch.utils.data.dataloader import DataLoader
        # return isinstance(dataset.src, DataLoader)
        str_type = str(dataset.src.__class__.__mro__)
        return '.DataLoader' in str_type and 'torch.' in str_type


class KerasDatasetObject(Identifier):
    """
    Keras Predefined dataset
    https://www.tensorflow.org/api_docs/python/tf/keras/datasets
    """
    FORMAT = DatasetFormat.KERAS_DATASET

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True

        ds = dataset.src
        # Keras dataset is a 2x2 metric of tuple
        # ds[0] is for training , ds[0][0] is x and ds[0][1] is y
        # ds[0] is for testing  , ds[1][0] is x and ds[1][1] is y
        # each record is a np.ndarray object
        if isinstance(ds, (tuple, list)):
            if len(ds) == 2 and len(ds[0]) == 2 and len(ds[1]) == 2:
                if all([isinstance(x, np.ndarray) for x in [ds[0][0], ds[0][1],
                                                            ds[1][0], ds[1][1]]]):
                    return True
        return False


class TFDSPrefetchObject(Identifier):
    """
    Use file extension and magic number to identify the file
    """
    FORMAT = DatasetFormat.TFDS_PREFETCH

    @classmethod
    def is_me(cls, dataset):
        if dataset.format == cls.FORMAT:
            return True
        str_type = str(type(dataset.src))
        return '.PrefetchDataset' in str_type and 'tensorflow.' in str_type
