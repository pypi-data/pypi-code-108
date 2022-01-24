from datetime import datetime
from decimal import Decimal
from io import BytesIO

import numpy as np  # type: ignore
import pyarrow  # type: ignore
import pyarrow as pa  # type: ignore


class ArbitraryBinaryArray:
    def __init__(self, val):
        self.val = val

    def __arrow_array__(self, type=None):
        # convert the underlying array values to a pyarrow Array
        mem_file = BytesIO()
        np.save(mem_file, self.val)  # noqa
        return pa.array([bytearray(mem_file.getvalue())], pa.binary())


DESERIALIZE_SEQUENCE_OPS = {
    "SELECT_column": lambda x: getattr(x, "column")(DEFAULT_SERIALIZED_COLUMN_NAME),
    "NATIVE_dict": lambda x: x.to_pandas().to_dict("records"),
    "NATIVE_list": lambda x: x.to_pylist(),
    "FINAL_list": lambda x: list(x),
    "FINAL_tuple": lambda x: tuple(x),
    "FINAL_first": lambda x: x[0],
}

NATIVE_TO_ARROW = {
    int: pyarrow.int8(),
    list: pyarrow.list_,
    float: pyarrow.float64(),
    Decimal: pyarrow.decimal128,
    str: pyarrow.string(),
    dict: pyarrow.struct,
    datetime: pyarrow.timestamp,
}

DEFAULT_SERIALIZED_COLUMN_NAME = "SerializedColumn_gen"
