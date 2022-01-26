"""
Utility functions for serialization
"""
import functools
import json
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

import pyarrow  # type: ignore
from pyarrow import json as j


def _serialize_dicts_or_list_of_dicts(
    values: Union[Sequence[Dict[Any, Any]], Dict[Any, Any]]
) -> pyarrow.Table:
    mem_file = BytesIO()
    if isinstance(values, dict):
        values = [values]
    for item in values:
        mem_file.write(json.dumps(item).encode())
    mem_file.seek(0)
    return j.read_json(mem_file)


def _get_final_serializer(
    initial_type: Type[Any], final_type: Type[Any]
) -> Optional[str]:
    if initial_type != final_type:
        if initial_type == list:
            return "NATIVE_list"
        if initial_type == tuple:
            return "FINAL_tuple"
        if initial_type == dict:
            return "FINAL_first"
        raise ValueError()
    return None


def add_deserializing_metadata(
    table: pyarrow.Table,
    *,
    deserializers: Optional[List[str]] = None,
    serializing_cls: Optional[str] = None
) -> pyarrow.Table:
    """add deserializing metadata"""
    metadata: Dict[str, Union[str, bytes]] = {}
    if deserializers:
        metadata["DESERIALIZERS"] = json.dumps(deserializers).encode()
    if serializing_cls:
        metadata["CLS"] = serializing_cls
    return _replace_table_with_metadata(table=table, metadata=metadata)


def _replace_table_with_metadata(
    table: pyarrow.Table, metadata: Dict[Any, Any]
) -> pyarrow.Table:
    final = (
        {**table.schema.metadata, **metadata}
        if table.schema.metadata
        else metadata
    )
    return table.replace_schema_metadata(metadata=final)


def inject_metadata(serializer: Callable[..., Any]) -> Callable[..., Any]:
    """inject metadata into serializer"""

    @functools.wraps(serializer)
    def wraps(cls: Any, *args: Any, **kwargs: Any) -> Any:
        table: pyarrow.Table = serializer(cls, *args, **kwargs)
        table = add_deserializing_metadata(
            table=table, serializing_cls=cls.__name__
        )
        return table

    return wraps
