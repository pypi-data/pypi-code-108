from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntrySchemaDetailedType(Enums.KnownString):
    ENTRY = "entry"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntrySchemaDetailedType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntrySchemaDetailedType must be a string (encountered: {val})")
        newcls = Enum("EntrySchemaDetailedType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntrySchemaDetailedType, getattr(newcls, "_UNKNOWN"))
