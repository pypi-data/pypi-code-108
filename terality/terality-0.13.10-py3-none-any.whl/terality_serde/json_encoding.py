from dataclasses import dataclass
import json
from json import JSONDecodeError
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import pyarrow

from terality_serde import loads, dumps, SerdeMixin, SerializableEnum


def _get_first_non_loadable_value(array: pd.array):
    for val in array:
        try:
            json.loads(val)
        except JSONDecodeError:
            return val
    assert False, "This method should be called only if we are sure a value can't be json loaded"


def _get_first_non_dumpable_value(series: pd.Series):
    for val in series:
        try:
            json.dumps(val)
        except JSONDecodeError:
            return val
    assert False, "This method should be called only if we are sure a value can't be json dumped"


def instantiate_pandas_arrow_extension_types():
    """
    Pyarrow has a weird bug where for the following types, if you read a parquet using these types directly
    it will fail to load to the right pandas extension dtypes. However, if you already used these types
    manually, they will be "available" and the parquet loading will work fine
    """
    data_to_instantiate = [
        pd.arrays.PeriodArray([1], freq="M"),
        [pd.Interval(pd.Timestamp.now(), pd.Timestamp.now(), closed="left")],
    ]
    for data in data_to_instantiate:
        pyarrow.Table.from_pandas(pd.Series(data).to_frame("foo"))


class ArrayEncoding(SerializableEnum):
    MIXED = "MIXED"
    STRUCT = "STRUCT"
    DURATION = "DURATION"


JSONABLE_TYPES = (float, int, bool, str, type(None))


@dataclass
class DFParquetEncoding(SerdeMixin):
    index: List[Optional[ArrayEncoding]]
    cols: List[Optional[ArrayEncoding]]


def has_float_nan(array: Union[np.ndarray, pd.array]) -> bool:
    series = pd.Series(array)
    return series[series.isna()].apply(lambda x: isinstance(x, float)).any()


def has_only_jsonable_types(array: np.ndarray):
    series = pd.Series(array)
    return series.apply(lambda x: isinstance(x, JSONABLE_TYPES)).all()


def decode_struct_array(array: pd.array) -> pd.array:
    """
    - Can't use apply to avoid pandas auto-casting.
    - Can't use pd.array(data) because if data has tuples
      pandas thinks we want to build a 2D array.
    """

    data_decoded = [loads(val) for val in array]
    return pd.Series(data_decoded, dtype="object").array


def decode_mixed_array(array: pd.array) -> pd.array:
    """
    - Can't use apply to avoid pandas auto-casting.
    - Can't use pd.array(data) because if data has tuples
      pandas thinks we want to build a 2D array.
    """

    try:
        data_decoded = [json.loads(val) for val in array]
    except JSONDecodeError as e:
        val = _get_first_non_loadable_value(array)
        raise ValueError(
            f"{val} with type {type(val).__name__} can't be json-loaded - happened while decoding a Mixed array."
        ) from e

    return pd.Series(data_decoded, dtype="object").array


def encode_struct_array(array: pd.array) -> pd.array:
    """
    Force dtype to avoid pandas auto-casting (ex: datetime.datetime to pd.Timestamp).
    """

    series = pd.Series(array, dtype=array.dtype)
    return series.apply(dumps).array


def encode_mixed_array(array: pd.array) -> pd.array:
    """
    Force dtype to avoid potential pandas auto-casting.
    """

    series = pd.Series(array, dtype=array.dtype)
    try:
        return series.apply(json.dumps).array
    except JSONDecodeError as e:
        val = _get_first_non_dumpable_value(series)
        raise ValueError(
            f"{val} with type {type(val).__name__} can't be json-dumped - happened while decoding a Mixed array."
        ) from e


_encodings = {
    ArrayEncoding.MIXED: encode_mixed_array,
    ArrayEncoding.STRUCT: encode_struct_array,
    # pyarrow to parquet does not support duraiont[ns]
    ArrayEncoding.DURATION: lambda x: x.view("int64"),  # pandas says view and not astype
}

_decodings = {
    ArrayEncoding.MIXED: decode_mixed_array,
    ArrayEncoding.STRUCT: decode_struct_array,
    ArrayEncoding.DURATION: lambda array: pd.array(array.astype("m8[ns]")),
}


def encode_array_for_parquet(
    array: pd.api.extensions.ExtensionArray, array_encoding: Optional[ArrayEncoding], encode: bool
) -> pd.api.extensions.ExtensionArray:
    if array_encoding is None:
        return array

    # allow not raising on unknown encodings to not break the compatibility with old clients when we add
    # new encodings
    encoder = _encodings.get(array_encoding) if encode else _decodings.get(array_encoding)
    if encoder is None:
        return array

    return encoder(array)


def _endecode_json_index_inplace(
    df: pd.DataFrame, indices_encoding: List[Optional[ArrayEncoding]], encode: bool
) -> None:
    """
    Encode/Decode index levels which are either Mixed or Struct types.
    Mutates the input DataFrame.
    """
    if isinstance(df.index, pd.RangeIndex):
        # enconding will convert RangeIndex to Int64Index
        return

    assert len(indices_encoding) == df.index.nlevels
    new_arrays = [
        encode_array_for_parquet(df.index.get_level_values(level_num).array, index_encoding, encode)
        for level_num, index_encoding in enumerate(indices_encoding)
    ]

    if isinstance(df.index, pd.MultiIndex):
        df.index = pd.MultiIndex.from_arrays(new_arrays, names=df.index.names)
    else:
        assert len(new_arrays) == 1
        df.index = pd.Index(new_arrays[0], name=df.index.name)


def _endecode_json_columns_inplace(
    df: pd.DataFrame, cols_encoding: List[Optional[ArrayEncoding]], encode: bool
) -> None:
    """
    Encode/Decode columns which are either Mixed or Struct types.
    Mutates the input DataFrame.
    """
    assert len(cols_encoding) == len(df.columns)
    for col_num, col_need_encoding in enumerate(cols_encoding):
        array = df.iloc[:, col_num].array
        df.iloc[:, col_num] = encode_array_for_parquet(array, col_need_encoding, encode)


def decode_df_inplace(df: pd.DataFrame, encoding: DFParquetEncoding) -> None:
    _endecode_json_index_inplace(df, encoding.index, encode=False)
    _endecode_json_columns_inplace(df, encoding.cols, encode=False)


def encode_df_inplace(df: pd.DataFrame, encoding: DFParquetEncoding) -> None:
    _endecode_json_index_inplace(df, encoding.index, encode=True)
    _endecode_json_columns_inplace(df, encoding.cols, encode=True)
