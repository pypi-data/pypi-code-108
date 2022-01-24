from unittest.mock import MagicMock
import datetime

import dynamo_io as dio
from dynamo_io.tests import fixtures
import aok

record = fixtures.Foo(
    first_key="spam",
    second_key="ham",
    foo_bar=42,
    created_at=datetime.datetime(2021, 1, 1, 2, 3, 4, tzinfo=datetime.timezone.utc),
    updated_at=datetime.datetime(2021, 1, 1, 2, 3, 4, tzinfo=datetime.timezone.utc),
    expires_at=datetime.datetime(2021, 1, 1, 2, 3, 4, tzinfo=datetime.timezone.utc),
)


def test_upsert():
    """Should call the upsert function without error."""
    client = MagicMock()
    dio.upsert(
        client=client,
        table_name="foo",
        record=record,
    )
    observed = client.update_item.call_args[1]

    assert client.update_item.call_count == 1
    expected = aok.Okay(
        {
            "TableName": "foo",
            "Key": {"pk": {"S": "spam"}, "sk": {"S": "ham"}},
            "ExpressionAttributeNames": {
                "#k0": "foo_bar",
                "#k3": "created_at",
                "#k4": "updated_at",
                "#k5": "expires_at",
            },
            "ExpressionAttributeValues": {
                ":v0": {"N": "42"},
                ":v3": {"S": "2021-01-01T02:03:04Z"},
                ":v4": {"S": "2021-01-01T02:03:04Z"},
                ":v5": {"N": "1609466584"},
            },
            "UpdateExpression": (
                "SET #k0=:v0, #k3=if_not_exists(#k3, :v3), #k4=:v4, #k5=:v5"
            ),
            "ReturnValues": "ALL_NEW",
        }
    )
    expected.assert_all(observed)
