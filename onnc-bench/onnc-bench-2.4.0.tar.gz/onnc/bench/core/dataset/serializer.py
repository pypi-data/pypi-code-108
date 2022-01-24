from typing import Union, List
from abc import abstractmethod
from pathlib import Path
import shutil
import numpy as np
from loguru import logger

from .identifier import DatasetFormat, identify
from ..common import get_tmp_path
from .transformer import DatasetTransformer
from .dataset import Dataset


class SerializerRegistry(type):

    REGISTRY: List = []

    def __new__(cls, name, bases, attrs):

        new_cls = type.__new__(cls, name, bases, attrs)

        cls.REGISTRY.append(new_cls)
        return new_cls


class Serializer(DatasetTransformer, metaclass=SerializerRegistry):

    FORMAT: Union[None, DatasetFormat] = None

    @classmethod
    def is_me(cls, dataset: Dataset) -> bool:
        return identify(dataset) == cls.FORMAT

    @abstractmethod
    def transform(self, dataset: Dataset) -> Dataset:
        pass

    def serialize(self, dataset: Dataset, dest: Path) -> Dataset:
        self.add_param('dest', dest)  # type: ignore[attr-defined]
        return self.transform(dataset)


def serialize(dataset: Dataset, dest: Path):
    for serializer in Serializer.REGISTRY:
        if serializer.is_me(dataset):
            return serializer().serialize(dataset, dest)

    raise NotImplementedError(f"Unalble to identify {dataset.src}")


class FileSerializer(Serializer):

    FORMAT: DatasetFormat = DatasetFormat.NON_SPECIFIED

    def transform(self, dataset: Dataset):
        dest = self.get_param('dest')

        if dataset.src.is_file():
            shutil.copy(dataset.src, dest)
        else:
            raise Exception(
                f'src [`{dataset.src}`] should be a path to a file.')

        return Dataset(dest)

    def serialize(self, dataset: Dataset, dest: Path) -> Dataset:
        # return super().serialize(model, dest)
        self.add_param('dest', dest)  # type: ignore[attr-defined]
        m = self.transform(dataset)
        return m


class DirSerializer(Serializer):

    FORMAT: DatasetFormat = DatasetFormat.NON_SPECIFIED

    def transform(self, dataset: Dataset):
        dest = self.get_param('dest')

        if Path(dest).exists() and Path(dest).is_dir():
            raise Exception(f'dest `{dest}` should be a file path.')
        elif not Path(dest).exists:
            if dest[-1] in ['\\', '/']:
                raise Exception(f"dest `{dest}` should file path, not a dir")

        if dataset.src.is_dir():
            # Zip the dir if the model is in dir form
            tmp_path = Path(get_tmp_path()[:-1])
            shutil.make_archive(str(tmp_path), 'zip', dataset.src)
            shutil.move(str(tmp_path) + '.zip', dest)
        else:
            raise Exception(
                f'dataset source `{dataset.src}` should be a path to a dir.')

        return Dataset(dest)

    def serialize(self, dataset: Dataset, dest: Path) -> Dataset:
        # return super().serialize(model, dest)
        self.add_param('dest', dest)  # type: ignore[attr-defined]
        m = self.transform(dataset)
        return m

class PB(FileSerializer):

    FORMAT = DatasetFormat.PB


class NPY(FileSerializer):

    FORMAT = DatasetFormat.NPY


class NPYDIR(DirSerializer):

    FORMAT = DatasetFormat.NPYDIR


class NPZ(FileSerializer):

    FORMAT = DatasetFormat.NPZ


class NDARRAY(Serializer):

    FORMAT = DatasetFormat.NDARRAY

    def transform(self, dataset: Dataset):
        dest = self.get_param('dest')  # type: ignore[attr-defined]
        np.save(dest, dataset.src)
        shutil.move(dest.with_suffix('.npy'), dest)
        return Dataset(dest)


class TORCH_DATASET(Serializer):

    FORMAT = DatasetFormat.TORCH_DATASET

    def transform(self, dataset: Dataset):
        import numpy
        dest = self.get_param('dest')  # type: ignore[attr-defined]
        if isinstance(dataset.src.data, numpy.ndarray):
            dataset_npy = Dataset(dataset.src.data)
        else:
            dataset_npy = Dataset(
                dataset.src.data.numpy())  # type: ignore[union-attr]
        
        # Handle NHWC data
        if len(dataset_npy.src.shape) == 4 and dataset_npy.src.shape[-1] <= 3:
            dataset_npy.src = dataset_npy.src.transpose((0, 3, 1, 2))

        ndarray_serializer = NDARRAY()
        return ndarray_serializer.serialize(dataset_npy, dest)


class TORCH_DATALOADER(Serializer):

    FORMAT = DatasetFormat.TORCH_DATALOADER

    def transform(self, dataset: Dataset):
        dest = self.get_param('dest')  # type: ignore[attr-defined]
        dataset_torch = Dataset(dataset.src.dataset)  # type: ignore[union-attr]
        torchdataset_serializer = TORCH_DATASET()
        return torchdataset_serializer.serialize(dataset_torch, dest)


class KERAS_DATASET(Serializer):

    FORMAT = DatasetFormat.KERAS_DATASET

    def transform(self, dataset: Dataset):
        dest = self.get_param('dest')  # type: ignore[attr-defined]
        # Keras dataset is a 2x2 metric of tuple
        # ds[0] is for training , ds[0][0] is x and ds[0][1] is y
        # ds[0] is for testing  , ds[1][0] is x and ds[1][1] is y
        # each record is a np.ndarray object
        # hence, we use x of testing data here
        dataset_npy = Dataset(dataset.src[1][0])  #type: ignore[index]
        ndarray_serializer = NDARRAY()
        return ndarray_serializer.serialize(dataset_npy, dest)


class TFDS_PREFETCH(Serializer):

    FORMAT = DatasetFormat.TFDS_PREFETCH
    SAMPLE_NUM = 1000
    SHUFFLE_SIZE = 1024

    def transform(self, dataset: Dataset):
        LABEL_KEYS = ['label']

        import tensorflow_datasets as tfds  # type: ignore[import]

        dest = self.get_param('dest')  # type: ignore[attr-defined]
        try:
            sample_num = self.get_param(
                'sample_num')  #type: ignore[attr-defined]

            if not sample_num:
                logger.warning('Parameter `sample_num` is not set, '
                               'use default value `1000`')
                sample_num = self.SAMPLE_NUM
        except Exception as e:
            logger.warning(
                'Parameter `sample_num` is not set, use default value `1000`')
            sample_num = self.SAMPLE_NUM

        ds = [
            x for x in dataset.src.shuffle(  # type: ignore[union-attr]
                self.SHUFFLE_SIZE).take(sample_num).as_numpy_iterator()
        ]

        keys = list(ds[0].keys())
        if len(keys) > 1:
            try:
                for key in LABEL_KEYS:
                    keys.remove(key)
            except ValueError:
                pass

        if len(keys) > 1:
            try:
                data_key = self.get_param(
                    'data_key')  #type: ignore[attr-defined]
                if not data_key:
                    logger.warning(f'Parameter `data_key` is not set, '
                                   'use default value `{keys[0]}`')
                    data_key = keys[0]
            except Exception as e:
                logger.warning(f'Parameter `data_key` is not set, '
                               'use default value `{keys[0]}`')
                data_key = keys[0]
        else:
            data_key = keys[0]

        dataset_npy = Dataset(np.stack([x[data_key] for x in ds]))

        ndarray_serializer = NDARRAY()
        return ndarray_serializer.serialize(dataset_npy, dest)
