from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunCreatedEventEventType(Enums.KnownString):
    V2_ASSAYRUNCREATED = "v2.assayRun.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayRunCreatedEventEventType must be a string (encountered: {val})")
        newcls = Enum("AssayRunCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
