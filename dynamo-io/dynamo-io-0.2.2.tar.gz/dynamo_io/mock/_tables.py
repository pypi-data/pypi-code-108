import typing
from fnmatch import fnmatch

from dynamo_io import definitions
from dynamo_io import recorder
from dynamo_io.mock import _expressions
from dynamo_io import _deserializer


class Key(typing.NamedTuple):

    partition_key_value: str
    sort_key_value: typing.Optional[str]

    def sort_starts(self, prefix: str) -> bool:
        return bool(self.sort_key_value and self.sort_key_value.startswith(prefix))


class Row:
    def __init__(self, row: dict):
        self._row = row

    @property
    def value(self) -> dict:
        return self._row

    @property
    def primary_key(self) -> Key:
        return typing.cast(Key, self.get_key(definitions.Indexes.STANDARD))

    def get_key(self, index: definitions.Index) -> typing.Optional[Key]:
        pk = typing.cast(str, self.get_key_value(index.partition_key))
        sk = self.get_key_value(index.sort_key)

        ignores = (None, "", definitions.DELETE)
        if pk in ignores or sk in ignores:
            return None

        return Key(pk, sk)

    def get_key_value(self, name: typing.Optional[str]) -> typing.Optional[str]:
        return self.value.get(name, {}).get("S")

    def update(self, row_update: dict) -> "Row":
        self.value.update(row_update)

        keys_to_remove = [
            k for k, v in self.value.items() if v in ("", None, definitions.DELETE)
        ]
        for k in keys_to_remove:
            del self.value[k]

        return self

    def update_from_expression(
        self,
        expression: str,
        names: typing.Dict[str, str],
        values: typing.Dict[str, typing.Dict[str, typing.Any]],
    ) -> "Row":
        self._row = _expressions.row_update_from_expression(
            expression=expression,
            names=names,
            values=values,
            existing_row=self._row,
        )
        return self

    def to_dict(self) -> dict:
        return self.value.copy()

    def to_record(
        self,
        record_class: typing.Type["recorder.Record"],
    ) -> typing.Optional["recorder.Record"]:
        """Converts the row to the record class if it matches."""
        if not record_class.schema.matches(self.value):
            return None
        return record_class.from_row(self.value)

    def deserialize(self) -> dict:
        """Returns a deserialized version of the row."""
        lookups = definitions.TYPE_REVERSE_LOOKUP
        return {
            k: _deserializer.deserialize(
                v, definitions.Column(name=k, data_type=lookups[list(v.keys())[0]])
            )
            for k, v in self.value.items()
        }

    def is_find_match(self, needles: dict) -> bool:
        """Attempts to match find dictionary against this row."""
        for key, comparison in needles.items():
            if key not in self.value:
                return False
            data_type, raw_value = list(self.value[key].items())[0]
            value = _deserializer.unstringify(
                value=raw_value,
                dtype=definitions.TYPE_REVERSE_LOOKUP[data_type],
            )

            if data_type == "S" and not fnmatch(value, comparison):
                return False

            if data_type != "S" and value != comparison:
                return False

        return True


class MockTable:
    def __init__(
        self,
        partition_key: str = "pk",
        sort_key: typing.Optional[str] = "sk",
        first_global_index_key: typing.Optional[str] = "g1k",
        second_global_index_key: typing.Optional[str] = "g2k",
    ):
        self.partition_key = partition_key
        self.sort_key = sort_key
        self.first_global_index_key = first_global_index_key
        self.second_global_index_key = second_global_index_key
        self.rows: typing.Dict[Key, Row] = {}

    def all_records(
        self,
        record_class: typing.Type["recorder.Record"],
    ) -> typing.List["recorder.Record"]:
        """
        Returns all of the rows in the table that match the given record
        class.
        """
        return [
            record_class.from_row(r)
            for row in self.rows.values()
            if record_class.schema.matches(r := row.to_dict())
        ]

    def find_rows(self, needles: dict) -> typing.List[dict]:
        return [r.deserialize() for r in self.rows.values() if r.is_find_match(needles)]

    def find_records(
        self, needles: dict, record_class: typing.Type["recorder.Record"]
    ) -> typing.List["recorder.Record"]:
        """
        Returns records that match the specified needles and are of the
        record class type.
        """
        return [
            record_class.from_row(row.to_dict())
            for row in self.rows.values()
            if row.is_find_match(needles) and record_class.schema.matches(row.to_dict())
        ]

    def add(
        self,
        pk: str,
        sk: str,
        g1k: str = None,
        g2k: str = None,
        **kwargs: typing.Dict[str, typing.Any],
    ) -> "MockTable":
        row: typing.Dict[str, typing.Any] = {
            self.partition_key: {"S": pk},
            **kwargs,
        }
        if self.sort_key:
            row[self.sort_key] = {"S": sk}

        if g1k is not None and self.first_global_index_key:
            row[self.first_global_index_key] = {"S": g1k}
        if g2k is not None and self.second_global_index_key:
            row[self.second_global_index_key] = {"S": g2k}
        return self.add_row(row)

    def add_row(self, row: dict) -> "MockTable":
        new_row = Row(row)
        key = new_row.primary_key
        if key in self.rows:
            raise KeyError("Key already exists.")
        self.rows[key] = new_row
        return self

    def add_rows(self, *args: dict) -> "MockTable":
        for row in args:
            self.add_row(row)
        return self

    def add_record(self, record: "recorder.Record") -> "MockTable":
        return self.add_row(record.to_row())

    def add_records(self, *args: "recorder.Record") -> "MockTable":
        for record in args:
            self.add_record(record)
        return self

    def get_row_from_index(
        self,
        index: definitions.Index,
        key: Key,
    ) -> typing.Optional[dict]:
        iterator = (r.to_dict() for r in self.rows.values() if r.get_key(index) == key)
        return next(iterator, None)

    def update_row(self, row_update: typing.Dict["Key", "Row"]) -> "MockTable":
        row = Row(row_update)
        key = row.primary_key
        if key in self.rows:
            self.rows[key].update(row_update)
        else:
            self.rows[key] = row
        return self

    def update_record(self, record_update: "recorder.Record") -> "MockTable":
        return self.update_row(record_update.to_row())

    def update_rows(self, *args: dict) -> "MockTable":
        """Modifies the specified rows with the included values."""
        for row_update in args:
            self.update_row(row_update)
        return self

    def update_records(self, *args: "recorder.Record") -> "MockTable":
        for record_update in args:
            self.update_record(record_update)
        return self

    def delete_key(self, key: Key) -> "MockTable":
        """Removes the row with the specified key from the table store."""
        if key in self.rows:
            del self.rows[key]
        return self

    def delete_row(self, row: dict) -> "MockTable":
        """Removes the specified row from the internal table store."""
        removal_row = Row(row)
        key = removal_row.primary_key

        if key in self.rows:
            del self.rows[key]
        return self

    def delete_rows(self, *args: dict) -> "MockTable":
        """Removes the specified rows from the internal table store."""
        for row in args:
            self.delete_row(row)
        return self

    def delete_record(self, record: "recorder.Record") -> "MockTable":
        """Removes the specified record from the internal table store."""
        return self.delete_row(record.to_row())

    def delete_records(self, *args: "recorder.Record") -> "MockTable":
        """Removes the specified records from the internal table store."""
        for record in args:
            self.delete_record(record)
        return self

    def get_rows(
        self,
        partition_key_value: str,
        sort_key_starts: str = None,
    ) -> typing.List[Row]:
        """
        Returns a list of rows that share the specified partition key value.
        Optionally specify a sort key start to filter the results down to
        rows that have sort key starting with that value.
        """
        return [
            row
            for key, row in self.rows.items()
            if key.partition_key_value == partition_key_value
            and (key.sort_key_value or "").startswith(sort_key_starts or "")
        ]

    def get(self, key: Key) -> typing.Optional[Row]:
        """Returns the row with the specified key if it exists."""
        return self.rows.get(key, None)

    def get_record(
        self, key: Key, record_class: typing.Type["recorder.Record"]
    ) -> typing.Optional["recorder.Record"]:
        """
        Returns the matching record as the given record class if it exists
        or None otherwise.
        """
        row = self.get(key)
        return row.to_record(record_class) if row else None

    def assert_has_key(self, key: Key):
        """Raises an assertion error if the key does not exist in the table."""
        assert (
            key in self.rows
        ), f"""
            Expected to find a row in the table with the key:
              - Partition Key Value: "{key.partition_key_value}"
              - Sort Key Value: "{key.sort_key_value}"
            """

    def assert_row_values(self, key: Key, comparisons: dict):
        """Raises an assertion error if the comparison do not match the row."""
        row = self.rows.get(key)
        assert (
            row is not None
        ), f"""
            Expected to find a row in the table with the key:
              - Partition Key Value: "{key.partition_key_value}"
              - Sort Key Value: "{key.sort_key_value}"
            to compare values against, but none was found.
            """

        r = row.deserialize()
        for k, v in comparisons.items():
            if callable(v):
                v(k, r.get(k))
                continue

            assert (
                r.get(k) == v
            ), f"""
                Expected the row value for "{k}" to be "{v}", but instead
                it was "{r.get(k)}".
                """

    def assert_matching_row_values(
        self,
        partition_key_value: str,
        sort_key_starts: str,
        comparisons: dict,
        allow_no_matches: bool = False,
    ):
        """
        Raises an assert error if the comparisons do not match the rows
        with the matching partition key value and have sort key that
        starts with the given comparison.
        """
        matching_keys = [
            key
            for key in self.rows.keys()
            if key.partition_key_value == partition_key_value
            and key.sort_starts(sort_key_starts or "")
        ]
        assert (
            allow_no_matches or len(matching_keys) > 0
        ), f"""
            Expected to find 1 or more matching rows with the partition
            key value "{partition_key_value}" and with sort keys starting
            with "{sort_key_starts or ''}".
            """

        for key in matching_keys:
            self.assert_row_values(key, comparisons)
