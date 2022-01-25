from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class OptimizeCodonsGcContent(Enums.KnownString):
    ANY = "ANY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "OptimizeCodonsGcContent":
        if not isinstance(val, str):
            raise ValueError(f"Value of OptimizeCodonsGcContent must be a string (encountered: {val})")
        newcls = Enum("OptimizeCodonsGcContent", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(OptimizeCodonsGcContent, getattr(newcls, "_UNKNOWN"))
