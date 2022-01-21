from typing import Set

import numpy as np
from terality_serde import StructType

from . import ClassMethod, Struct, StructIterator


class ClassMethodNDArray(ClassMethod):
    _class_name: str = StructType.NDARRAY
    _pandas_class = np.ndarray
    _additional_class_methods: Set[str] = {"from_numpy"}


class NDArray(Struct, metaclass=ClassMethodNDArray):
    """
    This class allows ndarray to be passed as arguments in pandas function calls, but the numpy API is not supported (calling any numpy method on an NDArray instance will fail).
    """

    _pandas_class_instance = np.empty(0)
    _additional_methods: Set[str] = {"to_numpy", "get_range_auto"}
    _indexers: Set[str] = set()

    def tolist(self):
        ndarray = self._call_method(None, "to_numpy")
        return ndarray.tolist()

    def __iter__(self):
        return StructIterator(self)
