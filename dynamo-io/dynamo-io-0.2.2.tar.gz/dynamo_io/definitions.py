import dataclasses
import datetime
import typing


# This does not currently pass mypy due to the limitation outlined in:
# https://github.com/python/mypy/issues/5374
# Until then we ignore the type issues for now.
@dataclasses.dataclass(frozen=True)  # type: ignore
class ResponseType(typing.Protocol):

    request: dict

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        ...


@dataclasses.dataclass(frozen=True)
class Response:
    """Data structure."""

    #: Raw boto3 response.
    response: dict
    #: Source payload arguments that specified the interaction
    request: dict

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        """Returns a dictionary version of the object for debug logging."""
        return {"request": self.request, "response": self.response}


@dataclasses.dataclass(frozen=True)
class SingleRowResponse(Response):
    """..."""

    row: typing.Optional[typing.Dict[typing.Any, typing.Any]]

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        cleaned_response = {
            k: v for k, v in (self.response or {}).items() if k not in ("Item",)
        }

        cleaned_row = {
            k: f"{v[:128]}..." if isinstance(v, str) and len(v) > 150 else v
            for k, v in (self.row or {}).items()
        }

        return {
            "request": self.request,
            "response": cleaned_response,
            "row": cleaned_row,
        }


@dataclasses.dataclass(frozen=True)
class PagedRowResponse:
    """..."""

    request: dict
    pages: typing.Tuple[dict, ...]
    rows: typing.Tuple[dict, ...]

    @property
    def first_row(self) -> typing.Optional[dict]:
        return next(iter(self.rows or []), None)

    def iter_rows(self) -> typing.Iterator[dict]:
        return iter(self.rows or [])

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        cleaned_pages = []
        for page in self.pages or []:
            cleaned_pages.append(
                {k: v for k, v in page.items() if k not in ("Item", "Items")}
            )

        return {
            "request": self.request,
            "pages": cleaned_pages,
            "page_count": len(cleaned_pages),
            "row_count": len(self.rows or []),
        }


@dataclasses.dataclass(frozen=True)
class ScannedRowResponse(PagedRowResponse):
    """..."""

    completed: bool

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        cleaned_pages = []
        for page in self.pages or []:
            cleaned_pages.append(
                {k: v for k, v in page.items() if k not in ("Item", "Items")}
            )

        return {
            "completed": self.completed,
            "request": self.request,
            "pages": cleaned_pages,
            "page_count": len(cleaned_pages),
            "row_count": len(self.rows or []),
        }


class SpecialOperation(typing.NamedTuple):
    """..."""

    operation: str


DELETE = SpecialOperation(operation="delete")


class TypeHints:
    """..."""

    Boolean = typing.Optional[typing.Union[bool, SpecialOperation]]
    BinarySet = typing.Optional[
        typing.Union[
            typing.List[bytes],
            SpecialOperation,
        ]
    ]
    String = typing.Optional[typing.Union[str, SpecialOperation]]
    Bytes = typing.Optional[typing.Union[bytes, SpecialOperation]]
    Date = typing.Optional[
        typing.Union[
            datetime.date,
            SpecialOperation,
        ]
    ]
    Datetime = typing.Optional[
        typing.Union[
            datetime.datetime,
            SpecialOperation,
        ]
    ]
    Float = typing.Optional[typing.Union[float, SpecialOperation]]
    Integer = typing.Optional[typing.Union[int, SpecialOperation]]
    Index = typing.Optional[typing.Union[str, SpecialOperation]]
    StringSet = typing.Optional[
        typing.Union[
            typing.List[str],
            SpecialOperation,
        ]
    ]
    FloatSet = typing.Optional[
        typing.Union[
            typing.List[float],
            SpecialOperation,
        ]
    ]
    IntegerSet = typing.Optional[
        typing.Union[
            typing.List[int],
            SpecialOperation,
        ]
    ]
    Timestamp = typing.Optional[
        typing.Union[
            datetime.datetime,
            SpecialOperation,
        ]
    ]
    List = typing.Optional[typing.List[typing.Any]]
    Map = typing.Optional[typing.Dict[str, typing.Any]]
    KeyColumn = typing.Optional[str]


class DynamoType(typing.NamedTuple):
    """Data structure for a DynamoDB type."""

    name: str
    value: str


BOOLEAN_TYPE = DynamoType("boolean", "BOOL")
BINARY_SET_TYPE = DynamoType("binary_set", "BS")
BYTES_TYPE = DynamoType("bytes", "B")
DATE_TYPE = DynamoType("date", "S")
DATETIME_TYPE = DynamoType("datetime", "S")
LIST_TYPE = DynamoType("list", "L")
FLOAT_TYPE = DynamoType("float", "N")
FLOAT_SET_TYPE = DynamoType("float_set", "NS")
INTEGER_TYPE = DynamoType("integer", "N")
INTEGER_SET_TYPE = DynamoType("integer_set", "NS")
MAP_TYPE = DynamoType("map", "M")
STRING_TYPE = DynamoType("string", "S")
STRING_SET_TYPE = DynamoType("string_set", "SS")
TIMESTAMP_TYPE = DynamoType("timestamp", "N")


class DynamoTypes:
    """Enumerations for DynamoDB data types."""

    BOOLEAN = BOOLEAN_TYPE
    BINARY_SET = BINARY_SET_TYPE
    BYTES = BYTES_TYPE
    DATE = DATE_TYPE
    DATETIME = DATETIME_TYPE
    LIST = LIST_TYPE
    FLOAT = FLOAT_TYPE
    FLOAT_SET = FLOAT_SET_TYPE
    INTEGER = INTEGER_TYPE
    INTEGER_SET = INTEGER_SET_TYPE
    MAP = MAP_TYPE
    STRING = STRING_TYPE
    STRING_SET = STRING_SET_TYPE
    TIMESTAMP = TIMESTAMP_TYPE


TYPE_LIST = [
    BOOLEAN_TYPE,
    BINARY_SET_TYPE,
    BYTES_TYPE,
    DATE_TYPE,
    DATETIME_TYPE,
    LIST_TYPE,
    FLOAT_TYPE,
    FLOAT_SET_TYPE,
    INTEGER_TYPE,
    INTEGER_SET_TYPE,
    MAP_TYPE,
    STRING_TYPE,
    STRING_SET_TYPE,
    TIMESTAMP_TYPE,
]

TYPE_REVERSE_LOOKUP = {data_type.value: data_type for data_type in TYPE_LIST}


class Index(typing.NamedTuple):
    """Enumeration for Dynamo Index Types."""

    id: str
    name: typing.Optional[str]
    partition_key: str
    sort_key: typing.Optional[str] = None


STANDARD_INDEX = Index("standard", None, "pk", "sk")
PARTITION_G1_INDEX = Index("partition_g1", "partition_g1", "pk", "g1k")
PARTITION_G2_INDEX = Index("partition_g2", "partition_g2", "pk", "g2k")
PARTITION_G3_INDEX = Index("partition_g3", "partition_g3", "pk", "g3k")

INVERTED_INDEX = Index("inverted", "inverted", "sk", "pk")
SORT_G1_INDEX = Index("sort_g1", "sort_g1", "sk", "g1k")
SORT_G2_INDEX = Index("sort_g2", "sort_g2", "sk", "g2k")
SORT_G3_INDEX = Index("sort_g3", "sort_g3", "sk", "g3k")

G1_PARTITION_INDEX = Index("g1_partition", "g1_partition", "g1k", "pk")
G1_SORT_INDEX = Index("g1_sort", "g1_sort", "g1k", "sk")
G1_G2_INDEX = Index("g1_g2", "g1_g2", "g1", "g2")
G1_G3_INDEX = Index("g1_g3", "g1_g3", "g1", "g3")

G2_PARTITION_INDEX = Index("g2_partition", "g2_partition", "g2k", "pk")
G2_SORT_INDEX = Index("g2_sort", "g2_sort", "g2k", "sk")
G2_G1_INDEX = Index("g2_g1", "g2_g1", "g2", "g1")
G2_G3_INDEX = Index("g2_g3", "g2_g3", "g2", "g3")

G3_PARTITION_INDEX = Index("g3_partition", "g3_partition", "g3k", "pk")
G3_SORT_INDEX = Index("g3_sort", "g3_sort", "g3k", "sk")
G3_G1_INDEX = Index("g3_g1", "g3_g1", "g3", "g1")
G3_G2_INDEX = Index("g3_g3", "g3_g3", "g3", "g3")


class Indexes:
    """Possible indexes on tables, including GSI indexes."""

    STANDARD = STANDARD_INDEX
    PARTITION_G1 = PARTITION_G1_INDEX
    PARTITION_G2 = PARTITION_G2_INDEX
    PARTITION_G3 = PARTITION_G3_INDEX

    INVERTED = INVERTED_INDEX
    SORT_G1 = SORT_G1_INDEX
    SORT_G2 = SORT_G2_INDEX
    SORT_G3 = SORT_G3_INDEX

    G1_PARTITION = G1_PARTITION_INDEX
    G1_SORT = G1_SORT_INDEX
    G1_G2 = G1_G2_INDEX
    G1_G3 = G1_G3_INDEX

    G2_PARTITION = G2_PARTITION_INDEX
    G2_SORT = G2_SORT_INDEX
    G2_G1 = G2_G1_INDEX
    G2_G3 = G2_G3_INDEX

    G3_PARTITION = G3_PARTITION_INDEX
    G3_SORT = G3_SORT_INDEX
    G3_G1 = G3_G1_INDEX
    G3_G2 = G3_G2_INDEX


INDEXES_LIST = [
    STANDARD_INDEX,
    PARTITION_G1_INDEX,
    PARTITION_G2_INDEX,
    PARTITION_G3_INDEX,
    INVERTED_INDEX,
    SORT_G1_INDEX,
    SORT_G2_INDEX,
    SORT_G3_INDEX,
    G1_PARTITION_INDEX,
    G1_SORT_INDEX,
    G1_G2_INDEX,
    G1_G3_INDEX,
    G2_PARTITION_INDEX,
    G2_SORT_INDEX,
    G2_G1_INDEX,
    G2_G3_INDEX,
    G3_PARTITION_INDEX,
    G3_SORT_INDEX,
    G3_G1_INDEX,
    G3_G2_INDEX,
]


# This does not currently pass mypy due to the limitation outlined in:
# https://github.com/python/mypy/issues/5374
# Until then we ignore the type issues for now.
@dataclasses.dataclass(frozen=True)  # type: ignore
class ColumnType(typing.Protocol):
    """Structural typing protocol for Column types."""

    #: Name of the column.
    name: str
    #: Data type for the column.
    data_type: DynamoType
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False


@dataclasses.dataclass(frozen=True)
class Column:
    """Data structure for a column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Data type for the column.
    data_type: DynamoType
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False


@dataclasses.dataclass(frozen=True)
class StringColumn:
    """Data structure for a string-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class BooleanColumn:
    """Data structure for a boolean-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Boolean.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.BOOLEAN, init=False)


@dataclasses.dataclass(frozen=True)
class BinarySetColumn:
    """Data structure for a binary-set-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Binary Set.
    data_type: DynamoType = dataclasses.field(
        default=DynamoTypes.BINARY_SET, init=False
    )


@dataclasses.dataclass(frozen=True)
class BytesColumn:
    """Data structure for a bytes-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Bytes.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.BYTES, init=False)


@dataclasses.dataclass(frozen=True)
class DateColumn:
    """Data structure for a date-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Date.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.DATE, init=False)


@dataclasses.dataclass(frozen=True)
class DatetimeColumn:
    """Data structure for a datetime-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Datetime.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.DATETIME, init=False)


@dataclasses.dataclass(frozen=True)
class ListColumn:
    """Data structure for a list-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type List.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.LIST, init=False)


@dataclasses.dataclass(frozen=True)
class FloatColumn:
    """Data structure for a float-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Float.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.FLOAT, init=False)


@dataclasses.dataclass(frozen=True)
class FloatSetColumn:
    """Data structure for a float-set-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Float Set.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.FLOAT_SET, init=False)


@dataclasses.dataclass(frozen=True)
class IntegerColumn:
    """Data structure for a integer-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Integer.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.INTEGER, init=False)


@dataclasses.dataclass(frozen=True)
class IntegerSetColumn:
    """Data structure for a integer-set-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Integer Set.
    data_type: DynamoType = dataclasses.field(
        default=DynamoTypes.INTEGER_SET, init=False
    )


@dataclasses.dataclass(frozen=True)
class MapColumn:
    """Data structure that defines a map column containing children elements"""

    #: Name of the column.
    name: str
    #: Columns for the children of the map column.
    children: typing.Tuple[Column, ...]
    #: Name of the key in the table
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Map.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.MAP, init=False)


@dataclasses.dataclass(frozen=True)
class StringSetColumn:
    """Data structure for a string-set-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String Set.
    data_type: DynamoType = dataclasses.field(
        default=DynamoTypes.STRING_SET, init=False
    )


@dataclasses.dataclass(frozen=True)
class TimestampColumn:
    """Data structure for a timestamp-type column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Name of the key in the table. If not specified the name will match
    #: the name value. Use this for additional keys.
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type Timestamp.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.TIMESTAMP, init=False)


@dataclasses.dataclass(frozen=True)
class IndexedColumn:
    """Data structure for a column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: typing.Optional[str] = None
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class PartitionColumn:
    """Data structure for a partition key column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: str = dataclasses.field(default="pk", init=False)
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class SortColumn:
    """Data structure for a sort key column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: str = dataclasses.field(default="sk", init=False)
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class GlobalFirstColumn:
    """Data structure for a tertiary key column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: str = dataclasses.field(default="g1k", init=False)
    #: Whether or not the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class GlobalSecondColumn:
    """Data structure for a tertiary key column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: str = dataclasses.field(default="g2k", init=False)
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class GlobalThirdColumn:
    """Data structure for a quaternary key column within a DynamoDB table."""

    #: Name of the column.
    name: str
    #: Value prefix within the table records
    value_prefix: str
    #: Name of the key in the table
    key: str = dataclasses.field(default="g3k", init=False)
    #: Whether the field is computed instead of stored directly in the
    #: model. Computed fields will be written to the database record but not
    #: loaded back into the model.
    computed: bool = False
    #: Data type for the column. Will always be of type String.
    data_type: DynamoType = dataclasses.field(default=DynamoTypes.STRING, init=False)


@dataclasses.dataclass(frozen=True)
class Schema:
    """Data structure defining a DynamoDB table"""

    partition_key: PartitionColumn
    sort_key: typing.Optional[SortColumn]
    columns: typing.Tuple[ColumnType, ...]

    common: typing.Tuple[Column, ...] = dataclasses.field(
        init=False,
        default_factory=lambda: (
            Column(name="created_at", data_type=DynamoTypes.DATETIME),
            Column(name="updated_at", data_type=DynamoTypes.DATETIME),
            Column(name="expires_at", data_type=DynamoTypes.TIMESTAMP),
        ),
    )

    @property
    def all_columns(self) -> typing.Tuple[ColumnType, ...]:
        """Custom and common columns."""
        return tuple(list(self.columns) + list(self.common))

    def matches(self, row: dict) -> bool:
        """
        Determines if the specified row is a match for the schema.

        :param row:
            A DynamoDB row record.
        """
        pk_name = self._is_partition_key_prefix_match(row)
        if pk_name is None:
            return False

        sk_prefix_match, sk_name = self._is_sort_key_prefix_match(row)
        if not sk_prefix_match:
            return False

        return self._is_exact_match(row, pk_name, sk_name)

    def _is_partition_key_prefix_match(self, row: dict) -> typing.Optional[str]:
        """Match the partition key with the row and return the comparison."""
        partition_key_name = self.partition_key.key or "pk"
        partition_key = row[partition_key_name]["S"]
        is_match = partition_key.startswith(self.partition_key.value_prefix)
        return partition_key_name if is_match else None

    def _is_sort_key_prefix_match(self, row: dict) -> typing.Tuple[bool, str]:
        """Match the sort key with the row and return the comparison."""
        sort_key_name = getattr(self.sort_key, "key", None) or "sk"
        sort_key = row.get(sort_key_name, {}).get("S")
        value_prefix = getattr(self.sort_key, "value_prefix", None)
        is_mismatch = (
            (sort_key is None and self.sort_key)
            or (sort_key is not None and not self.sort_key)
            or (sort_key and value_prefix and not sort_key.startswith(value_prefix))
        )
        return not is_mismatch, sort_key_name

    def _is_exact_match(
        self,
        row: dict,
        partition_key_name: str,
        sort_key_name: str,
    ) -> bool:
        """Only match if all keys in the row are present in the schema."""
        key_names = (partition_key_name, sort_key_name)
        schema_keys = {c.key or c.name for c in self.all_columns}
        row_keys = {k for k in row.keys() if k not in key_names}
        mismatches = row_keys - schema_keys
        return len(mismatches) == 0
