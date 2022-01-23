"""
Nozomi
HTTP Content Type Module
author: hugh@blinkybeach.com
"""
from enum import Enum
from nozomi.http.abstract_headers import AbstractHeaders
from typing import TypeVar, Optional, Type

T = TypeVar('T', bound='ContentType')

_JSON = 'application/json'
_XML = 'application/xml'
_HTML = 'text/html'

_KNOWN = (_JSON, _XML, _HTML)


class ContentType(Enum):

    JSON = _JSON
    XML = _XML
    HTML = _HTML

    @classmethod
    def from_headers(
        cls: Type[T],
        headers: AbstractHeaders,
        header: str = 'content-type'
    ) -> Optional[T]:

        value = headers.value_for(header)
        if value is None:
            return None

        value = value.lower()

        if value not in _KNOWN:
            return None

        if value == _JSON:
            return cls.JSON

        if value == _XML:
            return cls.XML

        raise RuntimeError('Unexpected fall through')
