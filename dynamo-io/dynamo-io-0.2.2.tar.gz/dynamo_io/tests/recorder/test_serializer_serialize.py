import datetime
import typing

from pytest import mark

import dynamo_io as dio
from dynamo_io import _serializer

SCENARIOS = (
    (True, True, dio.DynamoTypes.BOOLEAN),
    (False, False, dio.DynamoTypes.BOOLEAN),
    (b"abc", b"abc", dio.DynamoTypes.BYTES),
    ("abc", b"abc", dio.DynamoTypes.BYTES),
    (
        ["abc", "abc"],
        [b"abc", b"abc"],
        dio.DynamoTypes.BINARY_SET,
    ),
    (
        [b"abc", b"abc"],
        [b"abc", b"abc"],
        dio.DynamoTypes.BINARY_SET,
    ),
    (datetime.date(2021, 2, 3), "2021-02-03", dio.DynamoTypes.DATE),
    (
        datetime.datetime(2021, 2, 3, 12, 34, 56),
        "2021-02-03T12:34:56Z",
        dio.DynamoTypes.DATETIME,
    ),
    (42.42, "42.42", dio.DynamoTypes.FLOAT),
    (
        [42.42, 24.24],
        ["42.42", "24.24"],
        dio.DynamoTypes.FLOAT_SET,
    ),
    (42, "42", dio.DynamoTypes.INTEGER),
    (
        [42, 24],
        ["42", "24"],
        dio.DynamoTypes.INTEGER_SET,
    ),
    ("spam", "spam", dio.DynamoTypes.STRING),
    (
        ["spam", "spam"],
        ["spam", "spam"],
        dio.DynamoTypes.STRING_SET,
    ),
    (
        datetime.datetime(2021, 2, 3, 12, 34, 56, tzinfo=datetime.timezone.utc),
        "1612355696",
        dio.DynamoTypes.TIMESTAMP,
    ),
)


@mark.parametrize("value, expected, data_type", SCENARIOS)
def test_serialize(value: str, expected: typing.Any, data_type: dio.DynamoType):
    """Should stringify the value based on the column data type."""
    column = dio.Column("foo", data_type)
    assert _serializer.serialize(value, column) == {data_type.value: expected}


def test_serialize_map():
    """Should serialize a map column."""
    column = dio.MapColumn(
        "foo",
        children=(
            dio.Column("a", dio.DynamoTypes.STRING),
            dio.Column("b", dio.DynamoTypes.BOOLEAN),
            dio.Column("c", dio.DynamoTypes.INTEGER),
        ),
    )
    data = {
        "a": "hello",
        "b": True,
        "c": 42,
    }

    assert _serializer.serialize(data, column) == {
        "M": {
            "a": {"S": "hello"},
            "b": {"BOOL": True},
            "c": {"N": "42"},
        }
    }


def test_serialize_none():
    """Should return None for a None value."""
    column = dio.Column("foo", dio.DynamoTypes.STRING)
    assert _serializer.serialize(None, column) is None
