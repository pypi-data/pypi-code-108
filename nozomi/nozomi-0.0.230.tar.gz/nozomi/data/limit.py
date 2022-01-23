"""
Nozomi
Limit Module
author: hugh@blinkybeach.com
"""
from nozomi.data.query_string_conforming import QueryStringConforming
from nozomi.http.query_string import QueryString
from nozomi.data.sql_conforming import SQLConforming
from nozomi.ancillary.immutable import Immutable
from typing import TypeVar, Type, Optional

T = TypeVar('T', bound='Limit')


class Limit(SQLConforming, QueryStringConforming):

    def __init__(self, magnitude: int) -> None:
        assert isinstance(magnitude, int)
        self._magnitude = magnitude
        return

    sql_representation = Immutable(lambda s: s.adapt_integer(s._magnitude))
    magnitude = Immutable(lambda s: s._magnitude)
    query_string_value = Immutable(lambda s: str(s._magnitude))

    @classmethod
    def from_arguments(
        cls: Type[T],
        arguments: QueryString,
        max_value: int = 20,
        min_value: int = 0
    ) -> T:

        magnitude = arguments.parse_int(
            key='limit',
            max_value=max_value,
            min_value=min_value
        )

        return cls(magnitude)

    @classmethod
    def optionally_from_arguments(
        cls: Type[T],
        arguments: QueryString,
        max_value: int = 20,
        min_value: int = 0,
        fallback_value: Optional[int] = 0
    ) -> Optional[T]:

        magnitude = arguments.optionally_parse_int(
            key='limit',
            max_value=max_value,
            min_value=min_value
        )

        if magnitude is not None:
            return cls(magnitude)

        if fallback_value is None:
            return None

        return cls(fallback_value)
