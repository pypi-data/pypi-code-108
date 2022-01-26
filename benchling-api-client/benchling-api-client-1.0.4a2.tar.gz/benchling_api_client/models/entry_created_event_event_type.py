from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntryCreatedEventEventType(Enums.KnownString):
    V2_ENTRYCREATED = "v2.entry.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntryCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntryCreatedEventEventType must be a string (encountered: {val})")
        newcls = Enum("EntryCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntryCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
