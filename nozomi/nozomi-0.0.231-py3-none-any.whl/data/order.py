"""
Nozomi
Order Module
author: hugh@blinkybeach.com
"""
from nozomi.http.parseable_data import ParseableData
from nozomi.errors.bad_request import BadRequest
from nozomi.ancillary.immutable import Immutable
from nozomi.data.sql_conforming import SQLConforming
from nozomi.data.codable import Codable
from typing import TypeVar, Type, Any, Optional

T = TypeVar('T', bound='Order')


class Order(SQLConforming, Codable):

    def __init__(
        self,
        ascending: bool
    ) -> None:

        self._ascending = ascending

        return

    sql_representation = Immutable(
        lambda s: b'asc' if s._ascending else b'desc'
    )
    ascending: bool = Immutable(lambda s: s._ascending)
    descending: bool = Immutable(lambda s: not s._ascending)

    def __str__(self) -> str:
        return 'asc' if self._ascending else 'desc'

    def encode(self) -> str:
        if self._ascending is True:
            return 'ascending'
        return 'descending'

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        if data == 'asc' or data == 'ascending':
            return cls(ascending=True)
        if data == 'desc' or data == 'descending':
            return cls(ascending=False)
        raise ValueError

    @classmethod
    def optionally_from_request(
        cls: Type[T],
        request_data: ParseableData,
        default_to: Optional[T] = None
    ) -> Optional[T]:

        order = request_data.optionally_parse_string(
            key='order',
            max_length=32
        )

        if order is None:
            return default_to

        if order.lower() == 'ascending':
            return cls(True)

        if order.lower() == 'descending':
            return cls(False)

        raise BadRequest('Acceptable `order` values: ascending, descending')

    @classmethod
    def from_request(
        cls: Type[T],
        request_data: ParseableData,
        default_to: Optional[T] = None
    ) -> T:

        order = cls.optionally_from_request(request_data, default_to)

        if order is None:
            raise BadRequest(
                'Supply order=[ascending|descending] parameter'
            )

        return order
