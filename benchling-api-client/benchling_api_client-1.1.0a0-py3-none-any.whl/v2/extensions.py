from enum import Enum, IntEnum
from typing import Any, TypeVar

import attr


class NotPresentError(Exception):
    path: str
    message: str
    parent_name: str

    def __init__(self, parent: Any, path: str):
        self.path = path
        self.parent_name = type(parent).__name__
        self.message = f"Attempted to read '{self.parent_name}.{self.path}', which is Unset"
        super().__init__(self.message)


@attr.s(auto_attribs=True)
class UnknownType:
    """
    Represents a polymorphic type that this version of the SDK is not aware of.

    Oftentimes in e.g. listing endpoints, many different types of an entity can be returned.  As new features are added,
    new types can be returned from that same endpoint, but given that the SDK may not have been updated to know how to
    deserialize them, this would normally cause an error during deserialization.  This prevents normal program flow in
    cases which could be otherwise written defensively: none of the fields are programmatically accessible if
    deserialization fails, but programs may opt to handle errors or use the information they do know how to work with if
    serialization is made to be more 'nice.'
    """

    value: Any


T = TypeVar("T")


class Enums:
    class UnknownString(str, Enum):
        @staticmethod
        def known() -> bool:
            return False

        def __eq__(self, obj: Any) -> bool:
            return obj is self

        def __ne__(self, obj: Any) -> bool:
            return obj is not self

    class KnownString(str, Enum):
        @staticmethod
        def known() -> bool:
            return True

    class UnknownInt(IntEnum):
        @staticmethod
        def known() -> bool:
            return False

        def __eq__(self, obj: Any) -> bool:
            return obj is self

        def __ne__(self, obj: Any) -> bool:
            return obj is not self

    class KnownInt(IntEnum):
        @staticmethod
        def known() -> bool:
            return True
