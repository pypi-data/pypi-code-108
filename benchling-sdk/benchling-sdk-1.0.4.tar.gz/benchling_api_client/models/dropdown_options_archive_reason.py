from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DropdownOptionsArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DropdownOptionsArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of DropdownOptionsArchiveReason must be a string (encountered: {val})")
        newcls = Enum("DropdownOptionsArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DropdownOptionsArchiveReason, getattr(newcls, "_UNKNOWN"))
