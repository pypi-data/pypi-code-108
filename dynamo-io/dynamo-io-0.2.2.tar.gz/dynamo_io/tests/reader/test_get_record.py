import datetime
import typing
from unittest.mock import MagicMock

import dynamo_io as dio
from dynamo_io.tests import fixtures


def test_get_record():
    """Should return the expected record result."""
    client = MagicMock()
    client.get_item.return_value = {
        "Item": {
            "pk": {"S": "123"},
            "sk": {"S": "321"},
            "foo_bar": {"N": "42"},
            "bar": {"S": "2021-02-03T00:00:00Z"},
        }
    }

    result = dio.get_record(
        client=client,
        table_name="foo",
        source=fixtures.Foo(first_key="123", second_key="321"),
    )
    record = typing.cast(fixtures.Foo, result.record)

    assert record.first_key == "123"
    assert record.second_key == "321"
    assert record.foo_bar == 42
    assert record.bar == datetime.datetime(2021, 2, 3, tzinfo=datetime.timezone.utc)
    assert record.baz is None


def test_get_record_none():
    """Should return null if no record exists."""
    client = MagicMock()
    client.get_item.return_value = {}
    result = dio.get_record(client, "foo", fixtures.Foo("a", "b"))
    assert result.record is None
