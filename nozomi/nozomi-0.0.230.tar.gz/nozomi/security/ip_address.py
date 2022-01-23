"""
Nozomi
IP Address Module
author: hugh@blinkybeach.com
"""
from nozomi.data.encodable import Encodable
from nozomi.http.headers import Headers
from nozomi.http.status_code import HTTPStatusCode
from nozomi.ancillary.immutable import Immutable
from nozomi.data.sql_conforming import SQLConforming
from nozomi.errors.error import NozomiError
from typing import TypeVar, Type, Optional

T = TypeVar('T', bound='IpAddress')


class IpAddress(SQLConforming, Encodable):
    """
    A client IP address, discerned from examining headers written by a
    network boundary, presumed to be HAProxy
    """

    def __init__(
        self,
        raw_address: str
    ) -> None:

        assert isinstance(raw_address, str)
        self._raw_address = raw_address
        return

    sql_representation = Immutable(lambda s: s.quote_string(s._raw_address))

    @classmethod
    def load_from_headers(
        cls: Type[T],
        request_headers: Headers,
        debug: bool = False,
        debug_address: str = None,
        boundary_header: str = 'X-Ip-At-Boundary'
    ) -> T:

        assert isinstance(debug, bool)

        if debug is True:
            assert isinstance(debug_address, str)
            return cls(debug_address)

        addresses = request_headers.getlist(boundary_header)

        # We presume that headers are being set by HAProxy. If these checks
        # fail, HAProxy is not configured properly.

        if len(addresses) != 1:
            raise NozomiError('Internal error', HTTPStatusCode.INTERNAL_ERROR)

        if len(addresses[0].split(',')) != 1:
            raise NozomiError('Internal error', HTTPStatusCode.INTERNAL_ERROR)

        return cls(addresses[0])

    @classmethod
    def from_headers(
        cls: Type[T],
        headers: Headers,
        boundary_ip_header: str,
        debug: bool = False,
        debug_address: Optional[str] = None
    ) -> T:

        if debug is True:
            assert isinstance(debug_address, str)
            return cls(debug_address)

        addresses = headers.getlist(boundary_ip_header)

        # We presume that headers are being set by HAProxy. If these checks
        # fail, HAProxy is not configured properly.

        if len(addresses) != 1:
            raise NozomiError('Internal error', HTTPStatusCode.INTERNAL_ERROR)

        if len(addresses[0].split(',')) != 1:
            raise NozomiError('Internal error', HTTPStatusCode.INTERNAL_ERROR)

        return cls(addresses[0])

    def encode(self) -> str:
        return self._raw_address

    def __str__(self) -> str:
        return self._raw_address
