import typing

from dynamo_io.mock import _conditioner
from dynamo_io.mock import _tables


class Condition(typing.NamedTuple):

    operation: str
    name_key: str
    comparison: typing.Union[str, typing.List[str]]


class Paginator:
    def __init__(self, table: _tables.MockTable):
        self._table = table

    def paginate(self, **kwargs) -> typing.List[dict]:
        raise NotImplementedError("Must be overwritten by children.")


class ScanPaginator(Paginator):
    def paginate(self, **kwargs) -> typing.List[dict]:
        return [{"Items": [r.to_dict() for r in self._table.rows.values()]}]


class QueryPaginator(Paginator):
    def paginate(self, **kwargs) -> typing.List[dict]:
        limit = kwargs.get("Limit") or len(self._table.rows)
        names = kwargs.get("ExpressionAttributeNames") or {}
        values = kwargs.get("ExpressionAttributeValues") or {}
        conditions = _conditioner.parse_expression(
            kwargs.get("KeyConditionExpression") or ""
        )

        matches = [
            r.to_dict()
            for r in self._table.rows.values()
            if _conditioner.is_query_match(r, conditions, names, values)
        ]

        return [{"Items": []}, {"Items": matches[:limit]}]
