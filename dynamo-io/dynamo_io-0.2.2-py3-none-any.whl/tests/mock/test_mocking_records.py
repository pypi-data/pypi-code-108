import dataclasses
import typing

import dynamo_io as dio
from dynamo_io import mock


@dataclasses.dataclass(frozen=True)
class Product(dio.Record):

    product: dio.TypeHints.KeyColumn = None
    line: dio.TypeHints.KeyColumn = None
    category: dio.TypeHints.String = None

    units: dio.TypeHints.Integer = None

    schema = dio.Schema(
        partition_key=dio.PartitionColumn("product", "prod:"),
        sort_key=dio.SortColumn("line", "line:"),
        columns=(
            dio.GlobalFirstColumn("category", "cat:"),
            dio.Column("units", dio.DynamoTypes.INTEGER),
        ),
    )


@dataclasses.dataclass(frozen=True)
class Store(dio.Record):

    store_id: dio.TypeHints.String = None
    region: dio.TypeHints.String = None

    employees: dio.TypeHints.Integer = None

    schema = dio.Schema(
        partition_key=dio.PartitionColumn("store_id", "store:"),
        sort_key=dio.SortColumn("region", "region:"),
        columns=(dio.Column("employees", dio.DynamoTypes.INTEGER),),
    )


def test_e2e():
    """Should behave as expected."""
    client = mock.MockDynamoClient()

    dio.upsert(
        client=client,
        table_name="NA",
        record=Product(
            product="prod:snickers", line="line:candy-bar", category="cat:candy"
        ),
    )

    dio.insert_records(
        client=client,
        table_name="NA",
        records=[
            Store(store_id="store:seattle", region="region:northwest"),
            Store(store_id="store:boston", region="region:newengland"),
            Product(
                product="prod:mandms",
                line="line:candy-pieces",
                category="cat:candy",
            ),
        ],
    )

    dio.transacts(
        client=client,
        table_name="NA",
        puts=[
            Product(
                product="prod:twix",
                line="line:candy-bar",
                category="cat:candy",
            ),
            Product(
                product="prod:butter-finger",
                line="line:candy-bar",
                category="cat:candy",
            ),
            Product(
                product="prod:kit-kat",
                line="line:candy-bar",
                category="cat:candy",
            ),
            Product(
                product="prod:skittles",
                line="line:candy-pieces",
                category="cat:candy",
            ),
        ],
    )

    dio.transacts(
        client=client,
        table_name="NA",
        puts=[
            Store(
                store_id="store:mpls",
                region="region:midwest",
                employees=20,
            ),
            Store(
                store_id="store:portland",
                region="region:northwest",
                employees=20,
            ),
        ],
        updates=[
            Product(product="prod:twix", line="line:candy-bar", units=10),
        ],
    )

    result = dio.get_record(
        client=client,
        table_name="NA",
        source=Product(product="prod:twix", line="line:candy-bar"),
    )
    assert typing.cast(Product, result.record).units == 10

    result = dio.get_records_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="cat:candy",
        sort_key_starts="prod:s",
        index=dio.Indexes.G1_PARTITION,
        record_classes=[Product],
    )
    assert len(result.records) == 2

    result = dio.get_records_for_partition(
        client=client,
        table_name="NA",
        partition_key_value="cat:candy",
        before_sort_key="prod:n",
        index=dio.Indexes.G1_PARTITION,
        record_classes=[Product],
    )
    assert len(result.records) == 3

    result = dio.get_indexed_record(
        client=client,
        table_name="NA",
        source=Product(category="cat:candy", product="prod:kit-kat"),
        index=dio.Indexes.G1_PARTITION,
    )
    assert typing.cast(Product, result.record).product == "prod:kit-kat"

    result = dio.get_indexed_records(
        client=client,
        table_name="NA",
        source=Product(category="cat:candy", line="line:candy-pieces"),
        index=dio.Indexes.G1_SORT,
        limit=10,
    )
    assert len(result.records) == 2, "Expect two kinds of candy pieces"

    assert len(client.table.find_records({"pk": "prod:s*"}, Product)) == 2
    assert len(client.table.find_rows({"pk": "prod:s*"})) == 2

    assert len(client.table.all_records(Product)) == 6

    dio.remove(
        client=client,
        table_name="NA",
        record=Product(product="prod:kit-kat", line="line:candy-bar"),
    )

    result = dio.get_record(
        client=client,
        table_name="NA",
        source=Product(product="prod:kit-kat", line="line:candy-bar"),
    )
    assert result.row is None
