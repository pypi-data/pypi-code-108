from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunValidationStatus(Enums.KnownString):
    VALID = "VALID"
    INVALID = "INVALID"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunValidationStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayRunValidationStatus must be a string (encountered: {val})")
        newcls = Enum("AssayRunValidationStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunValidationStatus, getattr(newcls, "_UNKNOWN"))
