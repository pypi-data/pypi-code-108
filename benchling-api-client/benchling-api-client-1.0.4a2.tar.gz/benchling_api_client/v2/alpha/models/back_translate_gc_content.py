from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BackTranslateGcContent(Enums.KnownString):
    ANY = "ANY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BackTranslateGcContent":
        if not isinstance(val, str):
            raise ValueError(f"Value of BackTranslateGcContent must be a string (encountered: {val})")
        newcls = Enum("BackTranslateGcContent", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BackTranslateGcContent, getattr(newcls, "_UNKNOWN"))
