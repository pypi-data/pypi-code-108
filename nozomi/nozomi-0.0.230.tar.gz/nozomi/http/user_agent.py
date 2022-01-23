"""
Nozomi
UserAgent Module
author: hugh@blinkybeach.com
"""
from nozomi.http.headers import Headers
from nozomi.ancillary.immutable import Immutable
from nozomi.data.sql_conforming import SQLConforming
from typing import TypeVar, Type

T = TypeVar('T', bound='UserAgent')


class UserAgent(SQLConforming):

    def __init__(
        self,
        body: str
    ) -> None:

        self._body = body

        return

    string = Immutable(lambda s: s._body)
    sql_representation = Immutable(
        lambda s: s.dollar_quote_string(s.string).encode('utf-8')
    )

    @classmethod
    def from_headers(
        cls: Type[T],
        headers: Headers,
        fallback_to: str = 'Unavailable'
    ) -> T:

        body = headers.value_for('User-Agent')
        if body is None:
            return cls(body=fallback_to)

        return cls(body=body)
