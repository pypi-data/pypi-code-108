import functools
import json
from io import BytesIO
from typing import Dict, List, Sequence, Type, Union

import pyarrow  # type: ignore
from pyarrow import json as j


def _serialize_dicts_or_list_of_dicts(
    values: Union[Sequence[Dict], Dict]
) -> pyarrow.Table:
    mem_file = BytesIO()
    if isinstance(values, dict):
        values = [values]
    for item in values:
        mem_file.write(json.dumps(item).encode())
    mem_file.seek(0)
    return j.read_json(mem_file)


def _get_final_serializer(initial_type: Type, final_type: Type):
    if initial_type != final_type:
        if initial_type == list:
            return "NATIVE_list"
        elif initial_type == tuple:
            return "FINAL_tuple"
        elif initial_type == dict:
            return "FINAL_first"
        else:
            raise ValueError()
    return None


def add_deserializing_metadata(
    table: pyarrow.Table,
    *,
    deserializers: List[str] = None,
    serializing_cls: str = None
) -> pyarrow.Table:
    metadata: Dict[str, Union[str, bytes]] = {}
    if deserializers:
        metadata["DESERIALIZERS"] = json.dumps(deserializers).encode()
    if serializing_cls:
        metadata["CLS"] = serializing_cls
    return _replace_table_with_metadata(table=table, metadata=metadata)


def _replace_table_with_metadata(table: pyarrow.Table, metadata: Dict):
    final = {**table.schema.metadata, **metadata} if table.schema.metadata else metadata
    return table.replace_schema_metadata(metadata=final)


def inject_metadata(serializer):
    @functools.wraps(serializer)
    def wraps(cls, *args, **kwargs):
        table: pyarrow.Table = serializer(cls, *args, **kwargs)
        table = add_deserializing_metadata(table=table, serializing_cls=cls.__name__)
        return table

    return wraps
