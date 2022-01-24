import datetime
import typing

from dynamo_io import definitions


def _as_bytes(raw: typing.Union[str, bytes]) -> bytes:
    """Convert the source to bytes to conform to dynamoDB outputs."""
    if isinstance(raw, bytes):
        return raw

    if isinstance(raw, str):
        return raw.encode()

    return raw


def unstringify(value: str, dtype: definitions.DynamoType) -> typing.Any:
    """..."""
    types = definitions.DynamoTypes

    if dtype.name == types.TIMESTAMP.name:
        return datetime.datetime.utcfromtimestamp(int(value)).replace(
            tzinfo=datetime.timezone.utc
        )

    if dtype.name == types.DATETIME.name:
        return datetime.datetime.fromisoformat("{}+00:00".format(value.rstrip("Z")))

    if dtype.name == types.DATE.name:
        return datetime.datetime.fromisoformat(value).date()

    if dtype.name == types.BOOLEAN.name:
        return bool(value)

    if dtype.name in (types.FLOAT.name, types.FLOAT_SET.name):
        return float(value)

    if dtype.name in (types.INTEGER.name, types.INTEGER_SET.name):
        return int(value)

    if dtype.name in (types.BYTES.name, types.BINARY_SET.name):
        return _as_bytes(value)

    return value


def _deserialize_map_column(
    raw: typing.Any,
    column: "definitions.MapColumn",
) -> typing.Dict[str, typing.Any]:
    """Deserialize a map column into a flattened dictionary."""
    children = typing.cast(typing.Tuple[definitions.ColumnType, ...], column.children)
    raw_children = typing.cast(typing.Dict[str, typing.Any], raw)
    return {
        child.name: deserialize(raw_children[child.name], child)
        for child in children
        if child and raw_children[child.name] not in (None, "")
    }


def deserialize(
    value: typing.Dict[str, typing.Union[str, list, dict, bool]],
    column: definitions.ColumnType = None,
) -> typing.Any:
    """..."""
    if column is None or value[column.data_type.value] is None:
        return None

    raw = value[column.data_type.value]

    homogeneous_set_types = (
        definitions.DynamoTypes.BINARY_SET,
        definitions.DynamoTypes.FLOAT_SET,
        definitions.DynamoTypes.INTEGER_SET,
        definitions.DynamoTypes.STRING_SET,
    )

    if isinstance(column, definitions.MapColumn):
        return _deserialize_map_column(raw, column)
    elif column.data_type == definitions.DynamoTypes.MAP:
        lookups = definitions.TYPE_REVERSE_LOOKUP
        return {
            k: deserialize(
                data,
                definitions.Column(
                    name=k,
                    data_type=lookups[list(data.keys())[0]],
                ),
            )
            for k, data in typing.cast(typing.Dict[str, dict], raw).items()
        }

    if column.data_type in homogeneous_set_types:
        return [unstringify(v, column.data_type) for v in typing.cast(list, raw)]

    return unstringify(typing.cast(str, raw), column.data_type)
