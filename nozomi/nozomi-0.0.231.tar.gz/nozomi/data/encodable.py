"""
Nozomi
Encodable Module
author: hugh@blinkybeach.com
"""
from json import dumps
from typing import Any, TypeVar, Type, List
from nozomi.http.content_type import ContentType
from nozomi.data.encoder import Encoder
from nozomi.data.abstract_encodable import AbstractEncodable
from nozomi.data.xml import XML

T = TypeVar('T', bound='Encodable')


class Encodable(AbstractEncodable):
    """Abstract protocol defining an interface for encodable classes"""

    def encode(self) -> Any:
        """Return a JSON-serialisable form of the object"""
        raise NotImplementedError

    def serialise(self, format: ContentType = ContentType.JSON) -> str:
        """
        Return a string encoded representation of the object in the
        supplied format
        """
        if format == ContentType.JSON:
            return dumps(
                cls=Encoder,
                obj=self,
                separators=(',', ': '),
                sort_keys=True,
                indent=4
            )
        if format == ContentType.XML:
            return XML.data_to_xmlstring(self.encode())

        raise NotImplementedError(
            str(format.indexid) + ', ' + str(type(format))
        )

    @classmethod
    def encode_many(cls: Type[T], data: List[T]) -> List[Any]:
        """Return a list of JSON-serialisable forms"""
        return [d.encode() for d in data]

    @classmethod
    def serialise_many(cls: Type[T], data: List[T]) -> str:
        """Return json serialised list data"""
        return dumps(
            cls=Encoder,
            obj=data,
            separators=(',', ': '),
            sort_keys=True,
            indent=4
        )
