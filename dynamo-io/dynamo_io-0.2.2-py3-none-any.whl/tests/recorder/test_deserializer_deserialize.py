import datetime
import typing

from pytest import mark

import dynamo_io as dio
from dynamo_io import _deserializer

SCENARIOS = (
    (True, True, dio.DynamoTypes.BOOLEAN),
    (False, False, dio.DynamoTypes.BOOLEAN),
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
    ("2021-02-03", datetime.date(2021, 2, 3), dio.DynamoTypes.DATE),
    (
        "2021-02-03T12:34:56Z",
        datetime.datetime(2021, 2, 3, 12, 34, 56, tzinfo=datetime.timezone.utc),
        dio.DynamoTypes.DATETIME,
    ),
    ("42.42", 42.42, dio.DynamoTypes.FLOAT),
    (
        ["42.42", "24.24"],
        [42.42, 24.24],
        dio.DynamoTypes.FLOAT_SET,
    ),
    ("42", 42, dio.DynamoTypes.INTEGER),
    (
        ["42", "24"],
        [42, 24],
        dio.DynamoTypes.INTEGER_SET,
    ),
    ("spam", "spam", dio.DynamoTypes.STRING),
    (None, None, dio.DynamoTypes.STRING),
    (
        ["spam", "spam"],
        ["spam", "spam"],
        dio.DynamoTypes.STRING_SET,
    ),
    (
        "1612355696",
        datetime.datetime(2021, 2, 3, 12, 34, 56, tzinfo=datetime.timezone.utc),
        dio.DynamoTypes.TIMESTAMP,
    ),
)


@mark.parametrize("value, expected, data_type", SCENARIOS)
def test_deserialize(value: str, expected: typing.Any, data_type: dio.DynamoType):
    """Should deserialize the value based on the column data type."""
    column = dio.Column("foo", data_type)
    data = {data_type.value: value}
    assert _deserializer.deserialize(data, column) == expected


def test_deserialize_map():
    """Should deserialize a map column."""
    column = dio.MapColumn(
        "foo",
        children=(
            dio.Column("a", dio.DynamoTypes.STRING),
            dio.Column("b", dio.DynamoTypes.BOOLEAN),
            dio.Column("c", dio.DynamoTypes.INTEGER),
        ),
    )
    data = {
        "M": {
            "a": {"S": "hello"},
            "b": {"BOOL": "1"},
            "c": {"N": "42"},
        }
    }

    assert _deserializer.deserialize(data, column) == {
        "a": "hello",
        "b": True,
        "c": 42,
    }
