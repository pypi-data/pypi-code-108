from __future__ import annotations
from typing import Any, Dict, List, Callable, Type
import types
import pickle

from .dataset import Dataset, NDARRAYDataset

from . import __DATASET__


class DatasetTransformer():

    NAME = 'DatasetTransformer'

    def __init__(self):
        self.params = {}

    def transform(self, dataset: Type[Dataset]) -> object:
        return dataset

    def add_param(self, key: str, value: Any) -> None:
        self.params[key] = value

    def get_param(self, key: str) -> Any:
        return self.params[key]

    def set_transform(self, func: Callable, args: List = [],
                      kwargs: Dict = {}) -> None:

        """Set the transform func as given callback

        Args:
            func (Callable): preprocessor function, the output of the this
                             function has to be the preprocessed dataset.
            args (List): args for the preprocessor function, use `__DATASET__`
                         to indicate the dataset argument position

            kwargs (Dict): keword args for the preprocessor function

        Example:

            def _preprocess(dataset, min_val, max_val, enhancement=False):
              ....
              ....

            set_preprocessor(_preprocess,
                            ['__DATASET__', 1, 100],
                            {'enhancement': True}
                            )
        """

        def _transform(_self, dataset):

            # adapt __DATASET__
            for idx, i in enumerate(args):
                if i == __DATASET__:
                    args[idx] = dataset.src

            dataset.src = func(*args, **kwargs)
            return dataset

        setattr(self, 'transform', types.MethodType(_transform, self))

    def dump(self) -> bytes:
        return pickle.dumps(self)


class DatasetFormatTransformer(DatasetTransformer):
    NAME = 'DatasetFormatTransformer'


class ONNCDatasetToNumpy(DatasetFormatTransformer):
    NAME = 'ONNCDatasetToNumpy'

    def transform(self, dataset: Type[Dataset]) -> Type[Dataset]:
        import numpy as np

        # check if all elements are ndarray
        for obj in dataset.src:
            assert isinstance(obj, np.ndarray)

        data = np.concatenate(dataset.src, axis=0)

        dst_dataset = NDARRAYDataset(data)
        dst_dataset.clone_attributes(dataset)
        dst_dataset.src = data

        return dst_dataset

