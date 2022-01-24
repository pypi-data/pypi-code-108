import typing
from unittest.mock import MagicMock

import dynamo_io as dio
from dynamo_io.tests import fixtures


def test_get_indexed_record():
    """Should get indexed record via a query on a GSI."""
    client = MagicMock()
    paginator = client.get_paginator.return_value
    paginator.paginate.return_value = [
        {
            "Items": [
                {
                    "pk": {"S": "first:foo"},
                    "sk": {"S": "second:foo"},
                    "g1k": {"S": "third:foo"},
                    "foo_bar": {"N": "42"},
                }
            ]
        }
    ]

    result = dio.get_indexed_record(
        client=client,
        table_name="FAKE",
        source=fixtures.FooAndGsi(
            third_key="third:foo",
            first_key="first:foo",
        ),
        index=dio.Indexes.G1_PARTITION,
    )
    record = typing.cast(fixtures.FooAndGsi, result.record)

    assert record.first_key == "first:foo"
    assert record.second_key == "second:foo"
    assert record.third_key == "third:foo"
    assert record.foo_bar == 42

    query_kwargs = paginator.paginate.call_args[1]
    assert query_kwargs == {
        "TableName": "FAKE",
        "ExpressionAttributeNames": {"#k0": "g1k", "#k1": "pk"},
        "ExpressionAttributeValues": {
            ":v0": {"S": "third:foo"},
            ":v1": {"S": "first:foo"},
        },
        "KeyConditionExpression": "#k0=:v0 AND #k1=:v1",
        "Limit": 1,
        "IndexName": "g1_partition",
    }
