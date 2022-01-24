import datetime

import dynamo_io as dio
from dynamo_io.tests import fixtures

record = fixtures.Foo(
    first_key="spam",
    second_key="ham",
    foo_bar=42,
    bar=datetime.datetime(2021, 2, 3, tzinfo=datetime.timezone.utc),
    baz=dio.DELETE,
)

record_no_sort = fixtures.FooNoSort(
    first_key="spam",
    foo_bar=42,
    bar=datetime.datetime(2021, 2, 3, tzinfo=datetime.timezone.utc),
    baz=dio.DELETE,
)

record_with_gsi = fixtures.FooAndGsi(
    first_key="spam",
    second_key="ham",
    third_key="pam",
    foo_bar=42,
)


def test_dynamic_properties():
    """Should match the expected dynamic property values."""
    assert record.partition_key_value == "spam"
    assert record.sort_key_value == "ham"
    assert record.table_key == {
        "pk": {"S": "spam"},
        "sk": {"S": "ham"},
    }


def test_dynamic_properties_no_sort_key():
    """Should match the expected dynamic property values."""
    assert record_no_sort.partition_key_value == "spam"
    assert record_no_sort.sort_key_value is None
    assert record_no_sort.table_key == {
        "pk": {"S": "spam"},
    }


def test_to_row():
    """Should serialize to a DynamoDB row data structure."""
    expected = {
        "pk": {"S": "spam"},
        "sk": {"S": "ham"},
        "foo_bar": {"N": "42"},
        "bar": {"S": "2021-02-03T00:00:00Z"},
    }
    result = record.to_row()
    subset = {k: v for k, v in result.items() if k in expected}
    assert subset == expected


def test_to_row_gsi():
    """Should serialize to a DynamoDB row data structure."""
    expected = {
        "pk": {"S": "spam"},
        "sk": {"S": "ham"},
        "g1k": {"S": "pam"},
        "foo_bar": {"N": "42"},
    }
    result = record_with_gsi.to_row()
    subset = {k: v for k, v in result.items() if k in expected}
    assert subset == expected


def test_to_attribute_names():
    """Should produce the expected attribute names."""
    assert record.to_attribute_names() == {
        "#k0": "foo_bar",
        "#k1": "bar",
        "#k2": "baz",
        "#k3": "created_at",
        "#k4": "updated_at",
    }


def test_to_attribute_names_gsi():
    """Should produce the expected attribute names."""
    assert record_with_gsi.to_attribute_names() == {
        "#k0": "g1k",
        "#k1": "foo_bar",
        "#k2": "created_at",
        "#k3": "updated_at",
    }


def test_to_attribute_values():
    """Should produce the expected attribute values."""
    observed = record.to_attribute_values()
    assert observed[":v0"] == {"N": "42"}
    assert observed[":v1"] == {"S": "2021-02-03T00:00:00Z"}


def test_to_update_expression():
    """Should produce the expected update expression."""
    expected = (
        "SET #k0=:v0, #k1=:v1, #k3=if_not_exists(#k3, :v3), #k4=:v4 " "REMOVE #k2"
    )
    assert record.to_update_expression() == expected


def test_from_row():
    """Should to and from row identically."""
    new_record = fixtures.Foo.from_row(record.to_row())
    assert new_record.first_key == record.first_key
    assert new_record.second_key == record.second_key
    assert new_record.foo_bar == record.foo_bar
    assert new_record.bar == record.bar
    assert (
        new_record.baz is None
    ), """
        Expect the special operation to be ignored and the value
        set to None through the to and from record process.
        """
