from __future__ import annotations

from typing import Any, Union, Dict, List, Callable, Tuple, Type
from collections.abc import Iterable
from pathlib import Path
from collections import OrderedDict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import DataLayout

from ..common import get_class_name
from . import DatasetFormat


class Dataset:
    def __init__(self, raw_dataset: Union[Iterable, Iterable[Path], object]):
        self.src = raw_dataset  # Union[Iteraable, Path]
        self.y_label: OrderedDict[str, Union[int, float, str]] = OrderedDict()
        self.layout: Union[None, DataLayout] = None
        self.format: DatasetFormat = DatasetFormat.NON_SPECIFIED
        self.shape: Union[None, Tuple[int, ...]] = None
        # self._transformers: List = []

    # def exec_transformers(self) -> None:
    #     """To Trigger the transform pipeline
    #     """
    #     dataset = self
    #     for t in self._transformers:
    #         dataset = t.transform(dataset)
    #     self.src = dataset.src

    # def add_transformer(self, transformer: DatasetTransformer) -> None:
    #     self._transformers.append(transformer)

    def clone_attributes(self, dataset: Type[Dataset]) -> None:
        """Clone user defined attributes from input

        Iter all user-defined attributes and check if they have values.
        If the attribute of the destination object has value, then skip
        the clone.

        Args:
            dataset (Type[Dataset]): The dataset object to be cloned
        """
        _to_be_cloned: List = []
        for attr_name in dataset.__dict__:

            dst_value = getattr(self, attr_name)
            src_value = getattr(dataset, attr_name)

            if (isinstance(dst_value, OrderedDict)) or (isinstance(dst_value, List)):
                if len(dst_value) == 0:
                    _to_be_cloned.append([attr_name, src_value])

            elif dst_value is None:
                _to_be_cloned.append([attr_name, src_value])

        for attr_name, src_value in _to_be_cloned:
            setattr(self, attr_name, src_value)

    # def preprocess(self) -> None:
    #     """Alias for exec_transformers
    #     """
    #     self.exec_transformers()

    # def add_preprocessor(self, func: Callable, args: List = [],
    #                      kwargs: Dict = {}) -> None:
    #     """Add a preprocessor in the the pipeline

    #     Several preprocessors can be add into the pipeline

    #     Args:
    #         func (Callable): preprocessor function, the output of the this
    #                          function has to be the preprocessed dataset.
    #         args (List): args for the preprocessor function, use `__DATASET__`
    #                      to indicate the dataset argument position

    #         kwargs (Dict): keword args for the preprocessor function

    #     Example:

    #         def _preprocess(dataset, min_val, max_val, enhancement=False):
    #           ....
    #           ....

    #         add_preprocessor(_preprocess,
    #                         ['__DATASET__', 1, 100],
    #                         {'enhancement': True}
    #                         )
    #     """

    #     pt = PreprocessTransformer()
    #     pt.set_preprocessor(func, args, kwargs)
    #     self.add_transformer(pt)
    #     pass

    def dump(self) -> Dict:
        data = {
            "src": "",
            "y_label": self.y_label,
            "shape": self.shape,
            "layout": self.layout.dump() if self.layout is not None else None,
            "format": self.format.name
        }

        if isinstance(self.src, str):
            data["src"] = self.src
        elif isinstance(self.src, Path):
            data["src"] = str(self.src)
        else:
            data["src"] = get_class_name(self.src)

        return data

    def load(self, obj: Dict):
        raise NotImplementedError()


class ONNCDataset(Dataset):
    def __init__(self):
        super().__init__([])
        self.format = DatasetFormat.ONNC_DATASET


class NDARRAYDataset(Dataset):
    def __init__(self, raw_dataset: Union[Iterable]):
        super().__init__(raw_dataset)
        self.format = DatasetFormat.NDARRAY
