from enum import Enum
from typing import Iterable, List, Set


class ExtendedEnum(Enum):
    @classmethod
    def set(cls) -> Set:
        return {c.value for c in cls}

    @classmethod
    def list(cls) -> List:
        return [c.value for c in cls]

    @classmethod
    def names(cls: Iterable) -> List:
        return list(map(lambda c: c.name, cls))
