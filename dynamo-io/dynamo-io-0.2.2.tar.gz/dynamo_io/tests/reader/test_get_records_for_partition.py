import datetime
from unittest.mock import MagicMock

import dynamo_io as dio
from dynamo_io.tests import fixtures


def test_get_records_for_partition():
    """Should return the expected records."""
    client = MagicMock()
    paginator = client.get_paginator()
    paginator.paginate.return_value = [
        {
            "Items": [
                {
                    "pk": {"S": "first:abc"},
                    "sk": {"S": "second:123"},
                    "created_at": {"S": "2020-01-01T01:01:01Z"},
                    "updated_at": {"S": "2020-01-01T01:01:01Z"},
                    "foo_bar": {"N": "42"},
                },
                {
                    "pk": {"S": "first:abc"},
                    "sk": {"S": "second:123"},
                    "created_at": {"S": "2020-01-01T01:01:01Z"},
                    "updated_at": {"S": "2020-01-01T01:01:01Z"},
                    "does_not_exist": {"N": "42"},
                },
            ],
        },
        {
            "Items": [
                {
                    "pk": {"S": "first:abc"},
                    "baz": {"BOOL": True},
                    "created_at": {"S": "2020-01-01T01:01:01Z"},
                    "updated_at": {"S": "2020-01-01T01:01:01Z"},
                },
                {
                    "pk": {"S": "first:abc"},
                    "sk": {"S": "third:123"},
                    "bar": {"S": "2020-01-01T00:00:00Z"},
                    "created_at": {"S": "2020-01-01T01:01:01Z"},
                    "updated_at": {"S": "2020-01-01T01:01:01Z"},
                },
            ],
        },
    ]

    result = dio.get_records_for_partition(
        client=client,
        table_name="foo",
        partition_key_value="first:abc",
        record_classes=[fixtures.Foo, fixtures.FooNoSort],
    )
    records = result.records

    assert len(records) == 2
    assert records[0] == fixtures.Foo(
        first_key="first:abc",
        second_key="second:123",
        foo_bar=42,
        created_at=datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
    )
    assert records[1] == fixtures.FooNoSort(
        first_key="first:abc",
        baz=True,
        created_at=datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
    )
