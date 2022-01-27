from abc import ABC
from typing import TYPE_CHECKING, Any

from .exceptions import MongoValidationError

if TYPE_CHECKING:
    from .models import MongoModel


__all__ = ('Sum', 'Avg', 'Min', 'Count', 'Max')


class BasicDefaultAggregation(ABC):
    """Abstract class for Aggregation"""

    _operation: Any = None

    def __init__(self, field: str):
        self.field = field

    @property
    def operation(self) -> str:
        if not self._operation:
            raise NotImplementedError('implement _operation')
        return self._operation

    def _validate_field(self, mongo_model: 'MongoModel'):
        if self.field not in mongo_model.__fields__ and self.field != '_id':
            raise MongoValidationError(
                f'invalid field "{self.field}" for this model, field must be one of {list(mongo_model.__fields__.keys())}'
            )

    def _aggregate_query(self, mongo_model: 'MongoModel') -> dict:
        self._validate_field(mongo_model)
        query = {
            f'{self.field}__{self.operation}': {f'${self.operation}': f'${self.field}'}
        }
        return query


class Sum(BasicDefaultAggregation):
    _operation: Any = 'sum'


class Max(BasicDefaultAggregation):
    _operation: Any = 'max'


class Min(BasicDefaultAggregation):
    _operation: Any = 'min'


class Avg(BasicDefaultAggregation):
    _operation: Any = 'avg'


class Count(BasicDefaultAggregation):
    _operation: Any = 'count'

    def _aggregate_query(self, mongo_model: 'MongoModel') -> dict:
        self._validate_field(mongo_model)
        query = {
            "_id": f'${self.field}' if self.field != '_id' else None,
            f'count': {f'$sum': 1},
        }
        return query
