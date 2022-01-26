"""
Codecs for serializing objects
"""

import typing as t
from datetime import datetime
from decimal import Decimal
from io import BytesIO

import numpy as np
import pyarrow as pa  # type: ignore


class ArbitraryBinaryArray:  # pylint: disable=too-few-public-methods
    """ArbitraryBinaryArray"""

    def __init__(self, val: t.Any) -> None:
        self.val = val

    def __arrow_array__(self) -> pa.Array:
        # convert the underlying array values to a pyarrow Array
        mem_file = BytesIO()
        np.save(mem_file, self.val)  # type: ignore
        return pa.array([bytearray(mem_file.getvalue())], pa.binary())


DESERIALIZE_SEQUENCE_OPS: t.Dict[str, t.Callable[[t.Any], t.Any]] = {
    "SELECT_column": lambda x: getattr(x, "column")(
        DEFAULT_SERIALIZED_COLUMN_NAME
    ),
    "NATIVE_dict": lambda x: x.to_pandas().to_dict("records"),
    "NATIVE_list": lambda x: x.to_pylist(),
    "FINAL_list": list,
    "FINAL_tuple": tuple,
    "FINAL_first": lambda x: x[0],
}

NATIVE_TO_ARROW = {
    int: pa.int8(),
    list: pa.list_,
    float: pa.float64(),
    Decimal: pa.decimal128,
    str: pa.string(),
    dict: pa.struct,
    datetime: pa.timestamp,
}

DEFAULT_SERIALIZED_COLUMN_NAME = "SerializedColumn_gen"
