"""
Nozomi
Abstract Encodable Module
author: hugh@blinkybeach.com
"""
from typing import Any, TypeVar, Type, List
from nozomi.data.format import Format
from nozomi.data.format import Constants as Formats

T = TypeVar('T', bound='AbstractEncodable')


class AbstractEncodable:

    def encode(self) -> Any:
        """Return a JSON-serialisable form of the object"""
        raise NotImplementedError

    def serialise(self, format: Format = Formats.JSON) -> str:
        """
        Return a string encoded representation of the object in the
        supplied format
        """
        raise NotImplementedError

    @classmethod
    def serialise_many(cls: Type[T], data: List[T]) -> str:
        """Return json serialised list data"""
        raise NotImplementedError

    @classmethod
    def encode_many(cls: Type[T], data: List[T]) -> List[Any]:
        """Return a list of JSON-serialisable forms"""
        raise NotImplementedError
