import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import dynamo_io as dio
from dynamo_io.tests import fixtures

record = fixtures.Foo(
    first_key="spam",
    second_key="ham",
    foo_bar=42,
)

record_no_sort = fixtures.FooNoSort(
    first_key="spam",
    foo_bar=42,
    bar=datetime.datetime(2021, 2, 3),
)


@patch("time.sleep")
def test_insert_records(sleep: MagicMock):
    """Should insert records in the expected DynamoDB format."""
    client = MagicMock()
    client.batch_write_item.side_effect = [
        {"UnprocessedItems": [{}, {}]},
        {"UnprocessedItems": [{}]},
        {"UnprocessedItems": []},
    ]
    assert dio.insert_records(
        client=client,
        table_name="foo",
        records=[record, record_no_sort],
    )
    assert sleep.call_count == 3


@patch("time.sleep")
def test_insert_records_failed(sleep: MagicMock):
    """Should insert records in the expected DynamoDB format."""
    client = MagicMock()
    client.batch_write_item.return_value = {"UnprocessedItems": [{}]}

    with pytest.raises(RuntimeError):
        dio.insert_records(
            client=client,
            table_name="foo",
            records=[record, record_no_sort],
        )

    assert sleep.call_count == 10
