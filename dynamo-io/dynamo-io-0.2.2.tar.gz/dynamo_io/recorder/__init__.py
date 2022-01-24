import dataclasses
import datetime
import typing

from dynamo_io import definitions, _deserializer, _serializer


@dataclasses.dataclass(frozen=True)
class SingleRecordResponse(definitions.SingleRowResponse):
    """..."""

    record: typing.Optional["Record"]

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "record_type": str(type(self.record)),
            **super(SingleRecordResponse, self).to_debug_dict(),
        }


@dataclasses.dataclass(frozen=True)
class PagedRecordResponse(definitions.PagedRowResponse):
    """..."""

    records: typing.Tuple["Record", ...]

    @property
    def first_record(self) -> typing.Optional["Record"]:
        return next(iter(self.records or []), None)

    def iter_records(self) -> typing.Iterator["Record"]:
        return iter(self.records or [])

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        types = list(set([str(type(r)) for r in self.records or []]))
        return {
            "record_count": len(self.records or []),
            "record_types": types,
            **super(PagedRecordResponse, self).to_debug_dict(),
        }


@dataclasses.dataclass(frozen=True)
class ScannedRecordResponse(definitions.ScannedRowResponse):
    """..."""

    records: typing.Tuple["Record", ...]

    def to_debug_dict(self) -> typing.Dict[str, typing.Any]:
        types = list(set([str(type(r)) for r in self.records or []]))
        return {
            "record_count": len(self.records or []),
            "record_types": types,
            **super(ScannedRecordResponse, self).to_debug_dict(),
        }


@dataclasses.dataclass(frozen=True)
class Record:
    """
    Base class for cabinet DynamoDB Record models. Use this class by
    subclassing it and adding dataclass attributes representing the
    elements of the class. Also, the `schema` attribute needs to be
    overridden with the Schema definition specific to that Record model.
    The `schema` type hint must also always be `dio.SchemaType` as
    that type informs the DataClass that the schema is a class variable
    and should not be made into an instance variable dataclass field.
    A subclass would look like:

    ```
    @dataclasses.dataclass(frozen=True)
    class FooRecord:

        foo: dio.TypeHints.String
        bar: dio.TypeHints.String = None
        baz: dio.TypeHints.Datetime = None

        schema: dio.SchemaType = dio.Schema(
            partition_key=dio.IndexedColumn('foo', 'foo:'),
            sort_key=dio.IndexedColumn('bar', 'bar:'),
            columns=(
               dio.Column('baz', dio.DynamoTypes.DATETIME),
            )
        )
    ```

    The friendly names of the partition and sort keys, in this case `foo`
    and `bar` will be named `pk` and `sk` within the actual DynamoDB table
    as a generalization for a single-table store.

    Because the `schema` has a type hint of `dio.SchemaType`, they will
    be a class variable and shared among all instances of the same Record
    class. They are available on both the class `cls.schema` and instance
    `self.schema` references as needed within other methods.
    """

    #: Timestamp at which the record was first created.
    created_at: definitions.TypeHints.Datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.utcnow(),
    )
    #: Timestamp at which the record was last modified. Will
    #: auto-populate with the latest value by default when this
    #: record is created to always include it in the write
    #: process.
    updated_at: definitions.TypeHints.Datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.utcnow(),
    )
    #: Timestamp at which this record will be deleted
    #: automatically from the table, which is stored as a unix
    #: timestamp (integer seconds since epoch). This value
    #: should be null in production as it is used to keep data
    #: from persisting for the long-term in the development
    #: environment.
    expires_at: definitions.TypeHints.Timestamp = None
    #: Record DynamoDb schema structure.
    schema: typing.ClassVar[definitions.Schema] = definitions.Schema(
        partition_key=definitions.PartitionColumn("pk", "pk:"),
        sort_key=definitions.SortColumn("sk", "sk:"),
        columns=tuple(),
    )

    @property
    def columns(self) -> typing.Tuple[definitions.ColumnType, ...]:
        """All schema column definitions in the model."""
        return self.schema.all_columns

    @property
    def partition_key_value(self) -> str:
        """Value of the partition key in this Record."""
        return self.get_value_for(self.schema.partition_key)

    @property
    def sort_key_value(self) -> typing.Optional[str]:
        """Value of the sort key in this Record or None if does not exist."""
        if not self.schema.sort_key:
            return None
        return self.get_value_for(self.schema.sort_key)

    @property
    def table_key(self) -> typing.Dict[str, typing.Dict[str, dict]]:
        """
        DynamoDB table key dictionary containing the partition, and
        conditionally the sort key, as a single DynamoDB formatted
        dictionary. This is used to specify the key in DynamoDB
        operations on this Record.
        """
        keys = dict()
        pk_serialized = _serializer.serialize(
            self.get_value_for(self.schema.partition_key), self.schema.partition_key
        )
        if pk_serialized:
            keys["pk"] = pk_serialized

        if self.schema.sort_key:
            sk_serialized = _serializer.serialize(
                self.get_value_for(self.schema.sort_key),
                self.schema.sort_key,
            )
            if sk_serialized:
                keys["sk"] = sk_serialized

        return keys

    def get_value_for(
        self,
        column: typing.Optional[definitions.ColumnType],
    ) -> typing.Any:
        """
        Retrieves the value for the specified column, defaulting where such
        defaulting is desired.
        """
        if not column:
            return None

        value = getattr(self, column.name, None)
        if column.name in ("created_at", "updated_at") and value is None:
            return datetime.datetime.utcnow()
        return value

    def to_row(self) -> dict:
        """
        Creates a complete insertion row record for adding new records to
        a DynamoDB table. Empty values will be excluded from this record as
        DynamoDB does not accept null fields.
        """
        ignores = (None, "", definitions.DELETE)
        fields = {
            (column.key or column.name): _serializer.serialize(
                value=value, column=column
            )
            for column in self.columns
            if (value := self.get_value_for(column)) not in ignores
        }
        return {**self.table_key, **fields}

    def to_attribute_names(self) -> typing.Dict[str, str]:
        """
        Returns a dictionary containing expression attribute name mappings
        for the record. Expression names follow the format `#kN` where N is
        a positive integer based on the index of the key in the schema columns.
        Expression names are used by DynamoDB to prevent any actual key names
        from colliding with the DynamoDB expression language. Values set to
        `None` will not be included in the returned dictionary as they are
        intended to be left unchanged.
        """
        return {
            f"#k{index}": column.key or column.name
            for index, column in enumerate(self.columns)
            if self.get_value_for(column) is not None
        }

    def to_attribute_values(self) -> typing.Dict[str, typing.Dict[str, str]]:
        """
        Returns a dictionary containing expression attribute value mappings
        for the record. Expression values follow the format `:vN` where N is
        a positive integer based on the index of the key in the schema columns.
        Expression values are used by DynamoDB to prevent any actual key names
        from colliding with the DynamoDB expression language. Values set to
        `None` will not be included in the returned dictionary as they are
        intended to be left unchanged.
        """
        ignores = ("", None, definitions.DELETE)
        # noinspection PyUnboundLocalVariable
        return {
            f":v{i}": s
            for i, column in enumerate(self.columns)
            if (v := self.get_value_for(column)) not in ignores
            and (s := _serializer.serialize(v, column)) is not None
        }

    def to_update_expression(self) -> str:
        """
        Returns a string containing the DynamoDB expression language
        statement for upserting the record data into DynamoDB. It assumes
        the keys and values are specified as expression attribute name
        and value mappings using the `#kN` and `:vN` ordered key formats
        defined in the `to_attribute_names` and `to_attribute_values`
        methods. Values set to `None` will be left out of this expression
        and remain unchanged.
        """
        modifications = []
        removals = []

        for index, column in enumerate(self.columns):
            key_code = f"#k{index}"
            value_code = f":v{index}"
            value = self.get_value_for(column)

            if value is None:
                continue
            elif value in ("", definitions.DELETE):
                removals.append(key_code)
            elif column.name == "created_at":
                modifications.append(
                    f"{key_code}=if_not_exists({key_code}, {value_code})"
                )
            else:
                modifications.append(f"{key_code}={value_code}")

        set_expression = "SET {}".format(", ".join(modifications))
        remove_expression = "REMOVE {}".format(", ".join(removals))
        return " ".join(
            [
                set_expression if len(modifications) > 0 else "",
                remove_expression if len(removals) > 0 else "",
            ]
        ).strip()

    @classmethod
    def from_row(cls, row: dict) -> "Record":
        """
        Converts a DynamoDB row item response object into an instance of
        this Record class.
        """
        keys = {}

        pk = cls.schema.partition_key
        if not pk.computed:
            keys[pk.name] = _deserializer.deserialize(row[pk.key], pk)

        sk = cls.schema.sort_key
        if sk and not sk.computed:
            keys[sk.name] = _deserializer.deserialize(row[sk.key], sk)

        fields = {
            c.name: _deserializer.deserialize(row[c.key or c.name], c)
            for c in cls.schema.all_columns
            if (c.key or c.name) in row
            # Field names can duplicate names in the primary keys, e.g.
            # wanting to store accountId in both the key and a field. To
            # avoid issues, we ignore fields that are already populated by
            # the key (a many to one scenario).
            and c.name not in keys
            # Fields can be computed from other fields and are effectively
            # read only. Those fields should not be included in the record.
            and not c.computed
        }
        # noinspection PyArgumentList
        return cls(**keys, **fields)
