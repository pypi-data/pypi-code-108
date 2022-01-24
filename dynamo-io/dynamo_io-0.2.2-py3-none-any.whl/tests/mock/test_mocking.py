import dynamo_io as dio
from dynamo_io import mock as m

import pytest


@pytest.fixture
def client():
    c = m.MockDynamoClient()
    c.table.add_rows(
        {"pk": m.string("foo"), "sk": m.string("bar1"), "g1k": m.string("a")},
        {"pk": m.string("foo"), "sk": m.string("bar2"), "g1k": m.string("a")},
        {"pk": m.string("foo"), "sk": m.string("bar3"), "g1k": m.string("b")},
        {"pk": m.string("foo"), "sk": m.string("baz4"), "g1k": m.string("b")},
        {"pk": m.string("foo"), "sk": m.string("baz5"), "g1k": m.string("c")},
        {"pk": m.string("spam"), "sk": m.string("bar1"), "g1k": m.string("c")},
    )
    return c


def test_query_foo_baz(client: m.MockDynamoClient):
    """Should return all baz sort rows."""
    result = dio.get_rows_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="foo",
        sort_key_starts="baz",
    )
    assert len(result.rows) == 2


def test_query_foo_ba(client: m.MockDynamoClient):
    """Should return all rows starting with ba."""
    result = dio.get_rows_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="foo",
        sort_key_starts="ba",
    )
    assert len(result.rows) == 5


def test_query_spam_ba(client: m.MockDynamoClient):
    """Should return all rows starting with ba."""
    result = dio.get_rows_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="spam",
        sort_key_starts="ba",
    )
    assert len(result.rows) == 1


def test_query_bar1_foo_inverted(client: m.MockDynamoClient):
    """Should return all sk:bar1 rows where pk startswith foo."""
    result = dio.get_rows_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="bar1",
        sort_key_starts="foo",
        index=dio.Indexes.INVERTED,
    )
    assert len(result.rows) == 1


def test_query_a_foo_gsi(client: m.MockDynamoClient):
    """Should return expected rows from a GSI query."""
    result = dio.get_rows_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="c",
        sort_key_starts="foo",
        index=dio.Indexes.G1_PARTITION,
    )
    assert len(result.rows) == 1


def test_get_row_spam_bar1(client: m.MockDynamoClient):
    """Should return all rows starting with ba."""
    result = dio.get_row(
        client=client,
        table_name="NA",
        partition_key_value="spam",
        sort_key_value="bar1",
    )
    assert result.row["pk"]["S"] == "spam"
    assert result.row["sk"]["S"] == "bar1"


def test_scan_table(client: m.MockDynamoClient):
    """Should return all rows in the table."""
    result = dio.read_entire_table(client, "NA")
    assert len(result.rows) == 6


def test_get_indexed_rows(client: m.MockDynamoClient):
    """Should return teh foo a rows."""
    result = dio.get_indexed_rows(
        client=client,
        table_name="NA",
        partition_key_value="a",
        sort_key_value="foo",
        index=dio.Indexes.G1_PARTITION,
        limit=100,
    )
    assert len(result.rows) == 2


def test_get_indexed_row(client: m.MockDynamoClient):
    """Should return teh foo a rows."""
    result = dio.get_indexed_row(
        client=client,
        table_name="NA",
        partition_key_value="a",
        sort_key_value="foo",
        index=dio.Indexes.G1_PARTITION,
    )
    assert result.row["sk"]["S"] in ("bar1", "bar2")
