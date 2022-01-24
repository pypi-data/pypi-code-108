import dataclasses

import dynamo_io as dio


@dataclasses.dataclass(frozen=True)
class Foo(dio.Record):
    """Test class for Record functionality."""

    first_key: dio.TypeHints.KeyColumn = None
    second_key: dio.TypeHints.KeyColumn = None
    foo_bar: dio.TypeHints.Integer = None
    bar: dio.TypeHints.Datetime = None
    baz: dio.TypeHints.Boolean = None
    buzz: dio.TypeHints.Float = None

    schema: dio.SchemaType = dio.Schema(
        partition_key=dio.PartitionColumn("first_key", "first:"),
        sort_key=dio.SortColumn("second_key", "second:"),
        columns=(
            dio.Column("foo_bar", dio.DynamoTypes.INTEGER),
            dio.Column("bar", dio.DynamoTypes.DATETIME),
            dio.Column("baz", dio.DynamoTypes.BOOLEAN),
        ),
    )


@dataclasses.dataclass(frozen=True)
class FooRooted(dio.Record):
    """Test class for Record functionality."""

    first_key: dio.TypeHints.KeyColumn = None
    second_key: dio.TypeHints.KeyColumn = None
    foo_bar: dio.TypeHints.Integer = None
    bar: dio.TypeHints.Datetime = None
    baz: dio.TypeHints.Boolean = None
    buzz: dio.TypeHints.Float = None

    schema: dio.SchemaType = dio.Schema(
        partition_key=dio.PartitionColumn("first_key", ":first:"),
        sort_key=dio.SortColumn("second_key", ":second:"),
        columns=(
            dio.Column("foo_bar", dio.DynamoTypes.INTEGER),
            dio.Column("bar", dio.DynamoTypes.DATETIME),
            dio.Column("baz", dio.DynamoTypes.BOOLEAN),
        ),
    )


@dataclasses.dataclass(frozen=True)
class FooSlashes(dio.Record):
    """Test class for Record functionality."""

    first_key: dio.TypeHints.KeyColumn = None
    second_key: dio.TypeHints.KeyColumn = None
    foo_bar: dio.TypeHints.Integer = None
    bar: dio.TypeHints.Datetime = None
    baz: dio.TypeHints.Boolean = None
    buzz: dio.TypeHints.Float = None

    schema: dio.SchemaType = dio.Schema(
        partition_key=dio.PartitionColumn("first_key", "/first/"),
        sort_key=dio.SortColumn("second_key", "/second/"),
        columns=(
            dio.Column("foo_bar", dio.DynamoTypes.INTEGER),
            dio.Column("bar", dio.DynamoTypes.DATETIME),
            dio.Column("baz", dio.DynamoTypes.BOOLEAN),
        ),
    )


@dataclasses.dataclass(frozen=True)
class FooNoSort(dio.Record):
    """Test class for Record functionality with non sort key."""

    first_key: dio.TypeHints.KeyColumn = None
    foo_bar: dio.TypeHints.Integer = None
    bar: dio.TypeHints.Datetime = None
    baz: dio.TypeHints.Boolean = None
    buzz: dio.TypeHints.Float = None

    schema: dio.SchemaType = dio.Schema(
        partition_key=dio.PartitionColumn("first_key", "first:"),
        sort_key=None,
        columns=(
            dio.Column("foo_bar", dio.DynamoTypes.INTEGER),
            dio.Column("bar", dio.DynamoTypes.DATETIME),
            dio.Column("baz", dio.DynamoTypes.BOOLEAN),
        ),
    )


@dataclasses.dataclass(frozen=True)
class FooAndGsi(dio.Record):
    """Test class for Record functionality with a GSI."""

    first_key: dio.TypeHints.KeyColumn = None
    second_key: dio.TypeHints.KeyColumn = None
    third_key: dio.TypeHints.KeyColumn = None
    foo_bar: dio.TypeHints.Integer = None

    schema: dio.SchemaType = dio.Schema(
        partition_key=dio.PartitionColumn("first_key", "first:"),
        sort_key=dio.SortColumn("second_key", "second:"),
        columns=(
            dio.GlobalFirstColumn("third_key", "third:"),
            dio.Column("foo_bar", dio.DynamoTypes.INTEGER),
        ),
    )
