from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class StageEntryCreatedEventEventType(Enums.KnownString):
    V2_ALPHASTAGEENTRYCREATED = "v2-alpha.stageEntry.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "StageEntryCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of StageEntryCreatedEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("StageEntryCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(StageEntryCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
