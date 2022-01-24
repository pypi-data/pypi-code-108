import datetime as _datetime
import typing as _typing

from dynamo_io import _serializer
from dynamo_io import definitions
from dynamo_io.mock import _paginators
from dynamo_io.mock._comparisons import is_anything  # noqa: F401
from dynamo_io.mock._comparisons import is_in  # noqa: F401
from dynamo_io.mock._comparisons import is_instance_of  # noqa: F401
from dynamo_io.mock._comparisons import is_iso  # noqa: F401
from dynamo_io.mock._comparisons import is_like  # noqa: F401
from dynamo_io.mock._comparisons import is_match  # noqa: F401
from dynamo_io.mock._comparisons import is_not_null  # noqa: F401
from dynamo_io.mock._comparisons import is_optional  # noqa: F401
from dynamo_io.mock._paginators import Paginator  # noqa: F401
from dynamo_io.mock._tables import Key  # noqa: F401
from dynamo_io.mock._tables import MockTable  # noqa: F401
from dynamo_io.mock._tables import Row  # noqa: F401


def boolean(value: _typing.Union[bool, _typing.Any]) -> _typing.Optional[dict]:
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.BOOLEAN_TYPE,
        ),
    )


def string(value: str) -> _typing.Optional[dict]:
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.STRING_TYPE,
        ),
    )


def integer(value: _typing.Union[int, float]) -> _typing.Optional[dict]:
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.INTEGER_TYPE,
        ),
    )


def number(value: _typing.Union[int, float]) -> _typing.Optional[dict]:
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.FLOAT_TYPE,
        ),
    )


def timestamp(
    year: int = 2020,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> _typing.Optional[_typing.Dict[str, _typing.Any]]:
    value = _datetime.datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        0,
        tzinfo=_datetime.timezone.utc,
    )
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.TIMESTAMP_TYPE,
        ),
    )


def date_time(
    year: int = 2020,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> _typing.Optional[_typing.Dict[str, _typing.Any]]:
    value = _datetime.datetime(year, month, day, hour, minute, second)
    return _serializer.serialize(
        value,
        definitions.Column(
            name="",
            data_type=definitions.DATETIME_TYPE,
        ),
    )


class MockDynamoClient:
    def __init__(
        self,
        partition_key: str = "pk",
        sort_key: _typing.Optional[str] = "sk",
        first_global_index_key: _typing.Optional[str] = "g1k",
        second_global_index_key: _typing.Optional[str] = "g2k",
    ):
        self.partition_key = partition_key
        self.sort_key = sort_key
        self.first_global_index_key = first_global_index_key
        self.second_global_index_key = second_global_index_key
        self._table = MockTable(
            partition_key=partition_key,
            sort_key=sort_key,
            first_global_index_key=first_global_index_key,
            second_global_index_key=second_global_index_key,
        )

    @property
    def table(self) -> MockTable:
        return self._table

    def get_item(self, **kwargs) -> dict:
        key = Key(
            partition_key_value=kwargs["Key"][self.partition_key]["S"],
            sort_key_value=kwargs["Key"][self.sort_key]["S"],
        )
        row = self._table.rows.get(key)
        return {"Item": row.to_dict() if row else None, "ConsumedCapacity": {}}

    def update_item(self, **kwargs) -> dict:
        key = Key(
            partition_key_value=kwargs["Key"][self.partition_key]["S"],
            sort_key_value=kwargs["Key"][self.sort_key]["S"],
        )
        row = self._table.rows.get(key) or Row(kwargs["Key"].copy())
        row.update_from_expression(
            names=kwargs["ExpressionAttributeNames"],
            values=kwargs["ExpressionAttributeValues"],
            expression=kwargs["UpdateExpression"],
        )
        raw_row = row.to_dict()
        if key not in self._table.rows:
            self._table.add_row(raw_row)

        return {"Attributes": raw_row.copy(), "ConsumedCapacity": {}}

    def delete_item(self, **kwargs) -> dict:
        key = Key(
            partition_key_value=kwargs["Key"][self.partition_key]["S"],
            sort_key_value=kwargs["Key"][self.sort_key]["S"],
        )
        row = self._table.rows[key]
        self._table.delete_key(key)
        return {
            "Attributes": row.to_dict(),
            "ConsumedCapacity": {},
            "ItemCollectionMetrics": {},
        }

    def batch_write_item(self, **kwargs) -> dict:
        items = list((kwargs.get("RequestItems") or {}).values())[0]
        for item in items:
            if "PutRequest" in item:
                puts = item["PutRequest"]
                self._table.add_row(puts["Item"])
            elif "DeleteRequest" in item:
                deletes = item["DeleteRequest"]
                self._table.delete_key(
                    Key(
                        partition_key_value=deletes[self.partition_key]["S"],
                        sort_key_value=deletes[self.sort_key]["S"],
                    )
                )

        return {"UnprocessedItems": {}}

    def transact_write_items(self, **kwargs) -> dict:
        for item in kwargs["TransactItems"]:
            if "Put" in item:
                self._table.add_row(item["Put"]["Item"])
                continue

            key_data = (item.get("Delete") or item.get("Update"))["Key"]
            key = Key(
                partition_key_value=key_data[self.partition_key]["S"],
                sort_key_value=key_data[self.sort_key]["S"],
            )

            if "Delete" in item:
                self._table.delete_key(key)
                continue

            if key not in self._table.rows:
                self._table.add_row(key_data)

            args = item["Update"]
            row = self._table.rows[key]
            row.update_from_expression(
                expression=args["UpdateExpression"],
                names=args["ExpressionAttributeNames"],
                values=args["ExpressionAttributeValues"],
            )

        return {"ConsumedCapacity": [], "ItemCollectionMetrics": {}}

    def get_paginator(self, operation: str) -> "_paginators.Paginator":
        if operation == "query":
            return _paginators.QueryPaginator(self._table)
        elif operation == "scan":
            return _paginators.ScanPaginator(self._table)

        raise NotImplementedError(
            f'Pagination for "{operation}" is not currently supported.'
        )
