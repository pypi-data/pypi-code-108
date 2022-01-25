from __future__ import annotations
from dataclasses import dataclass
from functools import partial
from typing import Callable
import pickle
import sys

try:
    import cloudpickle
except ModuleNotFoundError as e:
    # pip does not know how to upgrade cloudpickle from the version we vendored to the 2.0 version.
    # In site-packages, it can leave a cloudpickle.dist-info folder without the cloudpickle folder.
    # In this situation, pip thinks cloudpickle is installed (and won't do anything), but Python
    # can't find the module source and will raise an ImportError.
    # See TER-976.
    raise ImportError(
        "The cloudpickle module is missing or in a corrupted state. Please uninstall it (with e.g `pip uninstall cloudpickle`) then reinstall Terality (with e.g `pip install terality`)."
    ) from e

import pandas as pd
from pandas.core.groupby import SeriesGroupBy, DataFrameGroupBy
from terality_serde.struct_types import STRUCT_TYPE_TO_PANDAS_CLASS

from . import SerdeMixin


_CLASS_NAME_TO_PANDAS_CLASS = {  # TODO replace "Index" by te.Index.__name__ etc
    "Index": pd.Index,
    "Int64Index": pd.Int64Index,
    "Float64Index": pd.Float64Index,
    "DatetimeIndex": pd.DatetimeIndex,
    "MultiIndex": pd.MultiIndex,
    "Series": pd.Series,
    "DataFrame": pd.DataFrame,
    "SeriesGroupBy": SeriesGroupBy,
    "DataFrameGroupBy": DataFrameGroupBy,
}


def _convert_terality_method_to_pandas(obj: Callable):
    """
    Need this conversion to apply the pandas function on the worker instead of the terality one.
    Exemple: when calling series.apply(te.isnull) we serde pd.isnull.

    However, this function has no effect regarding UDF using terality functions.
    For this case, the trick is to set sys.modules["terality"] = pd directly
    in the worker.
    """

    if isinstance(obj, partial):
        struct_type, accessor, method_name = obj.args
        if accessor is not None:
            raise ValueError(f"Function {obj} can not be serialized.")
        class_type = STRUCT_TYPE_TO_PANDAS_CLASS[struct_type]
    else:
        class_name = obj.__qualname__.split(".")[0]
        class_type = _CLASS_NAME_TO_PANDAS_CLASS[class_name]
        method_name = obj.__name__

    method_to_call = getattr(class_type, method_name)
    return method_to_call


@dataclass
class CallableWrapper(SerdeMixin):
    """Represent a user-supplied callable. THIS OBJECT CAN BE UNSAFE, READ THE DOCS!"""

    pickled_payload: bytes

    @classmethod
    def from_object(cls, obj: Callable) -> CallableWrapper:
        """Serialize the provided callable to a CallableWrapper.

        Internally, this uses the `cloudpickle` package and has the same limitations.

        Deserializing (even without running) such a serialized object can run arbitrary code.
        Only deserialize this in a safe sandboxed environment.
        """
        if isinstance(obj, type):
            # types are callable, but we don't support serializing them in this class
            raise TypeError("'obj' must not be a type")

        if isinstance(obj, partial):
            func = obj.func
        else:
            func = obj

        module_obj = None

        # numpy module is already impored in the worker so no need to pickle by value.
        # also, pickling it by value is buggy cf TER-563.
        if (
            hasattr(func, "__module__")
            and func.__module__ is not None
            and func.__module__ != "numpy"
        ):
            if func.__module__.split(".")[0] == "terality":
                obj = _convert_terality_method_to_pandas(obj)
                # pandas module already imported in the worker too.

            elif func.__module__ not in sys.modules:
                raise ValueError(
                    f"The provided callable module is '{func.__module__}', but it does not seem to be imported (not present in sys.modules). "
                    "Import this module in this Python session to be able to serialize this callable."
                )
            else:
                module_obj = sys.modules[func.__module__]
                cloudpickle.register_pickle_by_value(module_obj)  # type: ignore

        try:
            return cls(pickled_payload=cloudpickle.dumps(obj))  # type: ignore
        finally:
            if module_obj is not None:
                cloudpickle.unregister_pickle_by_value(module_obj)  # type: ignore

    def to_callable(self) -> Callable:
        """Return the deserialized callable. This function can run arbitrary user-supplied code and must only be run in a secure sandbox."""
        try:
            return pickle.loads(self.pickled_payload)
        except ModuleNotFoundError as e:
            raise ValueError(
                f"Can not deserialize this function, as it depends on a module not available in this execution environment: {str(e)}"
            ) from e
