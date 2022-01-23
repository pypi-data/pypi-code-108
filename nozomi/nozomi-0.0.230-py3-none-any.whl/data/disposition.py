"""
Nozomi
Disposition Module
author: hugh@blinkybeach.com
"""
from nozomi.data.codable import Codable
from nozomi.ancillary.immutable import Immutable
from nozomi.data.order import Order
from typing import TypeVar, Type, Any, Dict

T = TypeVar('T', bound='Disposition')


class Disposition(Codable):

    def __init__(
        self,
        sequence: int,
        count: int,
        limit: int,
        offset: int
    ) -> None:

        self._sequence = sequence
        self._count = count
        self._limit = limit
        self._offset = offset

        return

    sequence = Immutable(lambda s: s._sequence)
    count = Immutable(lambda s: s._count)
    limit = Immutable(lambda s: s._limit)
    offset = Immutable(lambda s: s._offset)

    def encode(self) -> Dict[str, int]:
        return {
            'sequence': self._sequence,
            'count': self._count,
            'limit': self._limit,
            'offset': self._offset
        }

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        return cls(
            sequence=data['sequence'],
            count=data['count'],
            limit=data['limit'],
            offset=data['offset']
        )
