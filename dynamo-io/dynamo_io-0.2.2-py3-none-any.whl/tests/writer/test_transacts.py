from unittest.mock import MagicMock

import dynamo_io as dio
from dynamo_io.tests import fixtures


def test_transacts():
    """Should call transact_write_items without error."""
    client = MagicMock()
    client.transact_write_items.return_value = {}

    dio.transacts(
        client=client,
        table_name="foo",
        puts=[
            fixtures.Foo(first_key="first:a", second_key="second:a"),
            fixtures.FooNoSort(first_key="first:b"),
        ],
        updates=[
            fixtures.Foo(first_key="first:c", second_key="second:c"),
            fixtures.FooNoSort(first_key="first:d"),
        ],
        deletes=[
            fixtures.Foo(first_key="first:e", second_key="second:e"),
            fixtures.FooNoSort(first_key="first:f"),
        ],
    )

    assert client.transact_write_items.call_count == 1
