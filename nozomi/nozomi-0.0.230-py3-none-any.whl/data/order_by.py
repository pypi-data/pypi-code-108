"""
Nozomi
Order By Module
author: hugh@blinkybeach.com
"""
from nozomi.data.query_string_conforming import QueryStringConforming
from nozomi.http.query_string import QueryString
from nozomi.data.codable import Codable
from nozomi.ancillary.immutable import Immutable
from nozomi.errors.bad_request import BadRequest
from nozomi.data.sql_conforming import SQLConforming
from typing import TypeVar, Type, Optional, Dict, Any, List

T = TypeVar('T', bound='OrderBy')


class OrderBy(SQLConforming, Codable, QueryStringConforming):
    """
    An object that may act as an order by term in a query
    """

    available: Dict[str, T] = NotImplemented

    def __init__(
        self,
        term: str,
        query_term: str
    ) -> None:

        self._term = term
        self._query_term = query_term

        return

    term = Immutable(lambda s: s._term)
    sql_representation = Immutable(lambda s: bytes(s._query_term, 'utf-8'))
    query_term = Immutable(lambda s: s._query_term)
    query_string_value = Immutable(lambda s: str(s._term))

    def __str__(self) -> str:
        return self._query_term

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        if not self._term == other._term:
            return False
        return True

    def encode(self) -> str:
        return self._term

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        return cls.available[data]

    @classmethod
    def optionally_from_arguments(
        cls: Type[T],
        arguments: QueryString,
        available: Optional[Dict[str, T]] = None,
        key: str = 'order_by',
        fallback_to: Optional[T] = None
    ) -> Optional[T]:

        if available is None:
            if not isinstance(cls.available, dict):
                raise RuntimeError('implement .available order by values')
            available = cls.available

        term = arguments.optionally_parse_string(key)

        if term is None:
            return fallback_to

        if term not in available.keys():
            raise BadRequest('Invalid {k} value. Valid values: {v}'.format(
                k=key,
                v=', '.join(available.keys())
            ))

        return available[term]

    @classmethod
    def optionally_many_from_arguments(
        cls: Type[T],
        arguments: QueryString,
        available: Optional[Dict[str, T]] = None,
        key: str = 'order_by',
        fallback_to: Optional[T] = None
    ) -> Optional[List[T]]:

        if available is None:
            if not isinstance(cls.available, dict):
                raise RuntimeError('implement .available order by values')
            available = cls.available

        values = arguments.parse_string(key).split(',')

        if values is None or len(values) < 1:
            return fallback_to

        parsed: List[T] = []

        for term in values:
            if term not in available.keys():
                raise BadRequest('Invalid {k} value. Valid values: {v}'.format(
                    k=key,
                    v=', '.join(available.keys())
                ))
            parsed.append(available[term])
            continue

        return parsed

    @classmethod
    def from_arguments(
        cls: Type[T],
        arguments: QueryString,
        available: Optional[Dict[str, T]] = None,
        key: str = 'order_by'
    ) -> T:

        order_by = cls.optionally_from_arguments(arguments, available, key)
        if order_by is None:
            raise BadRequest('Missing value for ' + key)

        return order_by
