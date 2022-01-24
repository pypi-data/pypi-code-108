import typing

from pytest import mark

import dynamo_io as dio
import dynamo_io.mock as dio_mock
from dynamo_io.tests import fixtures

_scenarios = (
    (fixtures.Foo, "first:", "second:"),
    (fixtures.FooRooted, ":first:", ":second:"),
    (fixtures.FooSlashes, "/first/", "/second/"),
)


@mark.parametrize("record_class, pk_prefix, sk_prefix", _scenarios)
def test_io(record_class: typing.Any, pk_prefix: str, sk_prefix: str):
    """Should read and write records as expected."""
    client = dio_mock.MockDynamoClient()

    pk = f"{pk_prefix}hello"
    sk = f"{pk_prefix}world"

    record = record_class(first_key=pk, second_key=sk)
    dio.insert_records(client, "foo", [record])

    assert dio.get_row(client, "foo", pk, sk).row
    assert dio.get_record(client, "foo", record).record
