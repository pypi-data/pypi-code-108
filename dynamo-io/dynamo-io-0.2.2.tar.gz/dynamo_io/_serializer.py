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


def _to_primitive(
    value: typing.Any,
    dtype: definitions.DynamoType,
) -> typing.Union[str, bool, bytes]:
    """
    Convert the specified value to its dynamoDB primitive value equivalent that is the
    necessary serialization to be valid when written to a DynamoDB table.
    """
    types = definitions.DynamoTypes

    if dtype.name == types.TIMESTAMP.name:
        return str(int(value.timestamp()))

    if dtype.name == types.DATETIME.name:
        if isinstance(value, datetime.datetime):
            value = value.replace(microsecond=0, tzinfo=datetime.timezone.utc)
        return f"{value.isoformat()}Z".replace("+00:00", "")

    if dtype.name == types.DATE.name:
        return value.isoformat()

    if dtype.name == types.BOOLEAN.name:
        return bool(value)

    if dtype.name in (types.FLOAT.name, types.FLOAT_SET.name):
        return str(float(value))

    if dtype.name in (types.INTEGER.name, types.INTEGER_SET.name):
        return str(int(value))

    if dtype.name in (types.BYTES.name, types.BINARY_SET.name):
        return _as_bytes(value)

    return str(value)


def serialize(
    value: typing.Any,
    column: definitions.ColumnType,
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """
    Returns a serialized attribute value for DynamoDB or None if the value is
    None or an empty string. Attribute values are dictionaries of the form:

    {DATA_TYPE: SERIALIZED_VALUE}

    where the DATA_TYPE is an enumerated value of known DynamoDB data types,
    and the SERIALIZED_VALUE is the value properly serialized.

    :param value:
        The value to be serialized into a DynamoDB value dictionary.
    :param column:
        The Column definition specifying the data type value for serialization.
    """
    if value is None or value == "":
        return None

    homogeneous_set_types = (
        definitions.DynamoTypes.BINARY_SET,
        definitions.DynamoTypes.FLOAT_SET,
        definitions.DynamoTypes.INTEGER_SET,
        definitions.DynamoTypes.STRING_SET,
    )

    key = column.data_type.value

    if isinstance(column, definitions.MapColumn):
        value = {
            child.name: serialize(value[child.name], child)
            for child in column.children
            if value[child.name] not in (None, "")
        }
        return {key: value}
    elif column.data_type in homogeneous_set_types:
        return {key: [_to_primitive(v, column.data_type) for v in value]}

    return {key: _to_primitive(value, column.data_type)}
