"""
Nozomi
Serialised Data Format Module
author: hugh@blinkybeach.com
"""
from nozomi.data.decodable import Decodable
from nozomi.ancillary.immutable import Immutable
from typing import TypeVar, Type, Any, Optional, Dict
from nozomi.data.sql_conforming import SQLConforming

T = TypeVar('T', bound='Format')


class Format(Decodable, SQLConforming):

    def __init__(
        self,
        indexid: int,
        name: str,
        header: str
    ) -> None:

        self._indexid = indexid
        self._name = name
        self._header = header

        return

    indexid: int = Immutable(lambda s: s._indexid)
    content_type_header: str = Immutable(lambda s: s._header)

    def __reduce__(self):
        return (Format, (
            self._indexid,
            self._name,
            self._header
        ))

    def encode(self) -> Dict[str, Any]:
        return {
            'indexid': self._indexid,
            'name': self._name,
            'header': self._header
        }

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        return Constants.ENUMERATIONS[data['indexid']]

    @classmethod
    def with_id(cls: Type[T], format_id: int) -> Optional[T]:
        if format_id in Constants.ENUMERATIONS:
            return Constants.ENUMERATIONS[format_id]
        return None

    sql_representation = Immutable(lambda s: s.adapt_integer(s.indexid))

    def __eq__(self, other):
        if other._indexid == self._indexid:
            return True
        return False


class Constants:

    JSON = Format(1, 'JSON', 'application/json')
    URL_ENCODED = Format(2, 'URL Encoded', 'application/x-www-form-urlencoded')
    MULTIPART_FORM = Format(3, 'Multipart Form', 'multipart/form-data')
    XML = Format(4, 'XML', 'application/xml')

    ENUMERATIONS = {
        JSON.indexid: JSON,
        URL_ENCODED.indexid: URL_ENCODED,
        MULTIPART_FORM.indexid: MULTIPART_FORM,
        XML.indexid: XML
    }
