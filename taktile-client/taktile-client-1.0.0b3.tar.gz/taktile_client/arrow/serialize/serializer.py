"""
Serializer classes
"""
import abc
import json
from io import BytesIO
from typing import Any, List, Optional, Sequence, Tuple, Type, Union, cast

import numpy
import numpy.typing as npt
import pandas  # type: ignore
import pyarrow  # type: ignore
from pandas.core.dtypes.inference import is_sequence  # type: ignore
from pydantic import BaseModel

from taktile_client.exceptions import SerializationError

from .codecs import (
    DEFAULT_SERIALIZED_COLUMN_NAME,
    DESERIALIZE_SEQUENCE_OPS,
    ArbitraryBinaryArray,
)
from .utils import (
    _get_final_serializer,
    _serialize_dicts_or_list_of_dicts,
    add_deserializing_metadata,
    inject_metadata,
)


class ObjectSerializer(abc.ABC):
    """Serialization for objects"""

    @classmethod
    @abc.abstractmethod
    def serialize(
        cls, value: Any, names: Optional[List[str]] = None
    ) -> Union[pyarrow.Table, BaseModel]:
        """Serialize an object"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, value: Any) -> Any:
        """Deserialize an object"""
        raise NotImplementedError


def is_valid_list_of_lists(lst: Union[List[Any], Tuple[Any, ...]]) -> bool:
    """Is this a list of lists of all the same length?"""
    is_list_of_lists = all(isinstance(i, list) for i in lst)
    if not is_list_of_lists:
        return False
    lengths = [len(i) for i in lst]
    return lengths.count(lengths[0]) == len(lengths)


class DataFrameSerializer(ObjectSerializer):
    """Serialization for DataFrames"""

    @classmethod
    def deserialize(cls, value: pyarrow.Table) -> pandas.DataFrame:
        return value.to_pandas()

    @classmethod
    @inject_metadata
    def serialize(
        cls, value: pandas.DataFrame, names: Optional[List[str]] = None
    ) -> pyarrow.Table:
        table = pyarrow.Table.from_pandas(value, preserve_index=True)
        return table


class SeriesSerializer(ObjectSerializer):
    """Serialization for Series"""

    @classmethod
    def find_idx(cls, table: pyarrow.Table) -> List[str]:
        """Find index"""
        return sorted(
            [
                col
                for col in table.column_names
                if col.startswith("__index_level_")
            ],
            key=lambda x: int("".join(s for s in x if s.isdigit())),
        )

    @classmethod
    def deserialize(cls, value: pyarrow.Table) -> pandas.Series:
        idxs = cls.find_idx(value)
        other_names = [c for c in value.column_names if c not in idxs]
        assert len(other_names) > 0
        name = other_names[0]
        if len(idxs) > 1:
            idx_values = [value.column(i).to_pandas().values for i in idxs]
            series_index = pandas.MultiIndex.from_arrays(idx_values)
        elif len(idxs) == 1:
            series_index = pandas.Index(
                value.column(idxs[0]).to_pandas().values
            )
        else:
            series_index = None
        return pandas.Series(
            value.column(name).to_pandas().values,
            index=series_index,
            name=name,
        )

    @classmethod
    @inject_metadata
    def serialize(
        cls, value: pandas.Series, names: Optional[List[str]] = None
    ) -> pyarrow.Table:
        as_df = pandas.DataFrame(value)
        tbl = pyarrow.Table.from_pandas(as_df, preserve_index=True)
        return tbl


class ArraySerializer(ObjectSerializer):
    """Serialization for Arrays"""

    @classmethod
    def deserialize(cls, value: pyarrow.Table) -> npt.NDArray[Any]:
        if len(value.columns) == 1:
            return cast(
                npt.NDArray[Any], value.column(0).to_pandas().to_numpy()
            )
        return cast(
            npt.NDArray[Any],
            numpy.concatenate(  # type: ignore
                [
                    value.column(i).to_pandas().to_numpy().reshape(-1, 1)
                    for i in range(len(value.columns))
                ],
                axis=1,
            ),
        )

    @classmethod
    @inject_metadata
    def serialize(
        cls, value: npt.NDArray[Any], names: Optional[List[str]] = None
    ) -> pyarrow.Table:
        arrow_arrays = []
        if value.ndim == 1:
            columns = 1
            arrow_arrays = [pyarrow.array(value)]
        elif value.ndim == 2:
            _, columns = value.shape
            for column in range(columns):
                arrow_arrays.append(pyarrow.array(value[:, column]))
        else:
            raise SerializationError("Must serialise using binary format")
        if not names:
            names = [str(i) for i in range(columns)]
        return pyarrow.Table.from_arrays(arrays=arrow_arrays, names=names)


class SequenceSerializer(ObjectSerializer):
    """Serialization for sequences"""

    @classmethod
    def deserialize(cls, value: pyarrow.Table) -> Any:
        pipeline = json.loads(
            value.schema.metadata[b"DESERIALIZERS"].decode("utf-8")
        )
        for function_ref in pipeline:
            value = DESERIALIZE_SEQUENCE_OPS[function_ref](value)
        return value

    @staticmethod
    def _serialize(
        value: Sequence[Any],
    ) -> Tuple[Union[pyarrow.Array, pyarrow.Table], Type[Any]]:
        if isinstance(value, (list, tuple)):
            if len(value) > 0:
                first = value[0]
                if isinstance(first, list):
                    is_valid = is_valid_list_of_lists(value)
                    if is_valid:
                        return pyarrow.array(value), list
                    raise SerializationError(
                        "Must serialise using binary format"
                    )
                if isinstance(first, dict):
                    return _serialize_dicts_or_list_of_dicts(value), list
                # more specific than numpy's is_sequence implementation
                if not is_sequence(first):
                    return pyarrow.array(value), list
            else:
                raise ValueError("Invalid inputs provided: empty sequence")
        if isinstance(value, dict):
            return _serialize_dicts_or_list_of_dicts(value), list
        raise SerializationError("Unsupported input type")

    @classmethod
    @inject_metadata
    def serialize(
        cls, value: Sequence[Any], names: Optional[List[str]] = None
    ) -> pyarrow.Table:
        intermediate, final_type = cls._serialize(value)
        final_deserializer = _get_final_serializer(
            initial_type=type(value), final_type=final_type
        )
        if isinstance(intermediate, pyarrow.Table):
            deserializer_pipeline = ["NATIVE_dict"]
            if final_deserializer:
                deserializer_pipeline.append(final_deserializer)

            intermediate = add_deserializing_metadata(
                intermediate, deserializers=deserializer_pipeline
            )

        elif isinstance(intermediate, pyarrow.Array):
            as_table = pyarrow.Table.from_arrays(
                [intermediate], names=[DEFAULT_SERIALIZED_COLUMN_NAME]
            )
            deserializer_pipeline = ["SELECT_column", "NATIVE_list"]
            if final_deserializer:
                deserializer_pipeline.append(final_deserializer)
            intermediate = add_deserializing_metadata(
                as_table, deserializers=deserializer_pipeline
            )
        else:
            raise SerializationError("Must serialize using binary format")
        return intermediate


class BinarySerializer(ObjectSerializer):
    """Fallback serializer"""

    @classmethod
    def deserialize(cls, value: pyarrow.Table) -> Any:
        val = value.to_pandas()[DEFAULT_SERIALIZED_COLUMN_NAME].values
        if not val:
            return None
        mem_file = BytesIO(val[0])
        return numpy.load(mem_file, allow_pickle=True)  # type: ignore

    @classmethod
    @inject_metadata
    def serialize(
        cls, value: Any, names: Optional[List[str]] = None
    ) -> pyarrow.Table:
        bin_schema = pyarrow.schema(
            [(DEFAULT_SERIALIZED_COLUMN_NAME, pyarrow.binary())]
        )
        arr = ArbitraryBinaryArray(val=value)
        deserializer_pipeline = ["SELECT_column"]
        intermediate = pyarrow.table([arr], schema=bin_schema)
        return add_deserializing_metadata(
            table=intermediate, deserializers=deserializer_pipeline
        )
