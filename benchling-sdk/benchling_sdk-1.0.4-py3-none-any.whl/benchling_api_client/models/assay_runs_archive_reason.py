from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunsArchiveReason(Enums.KnownString):
    ARCHIVED = "Archived"
    MADE_IN_ERROR = "Made in error"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunsArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayRunsArchiveReason must be a string (encountered: {val})")
        newcls = Enum("AssayRunsArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunsArchiveReason, getattr(newcls, "_UNKNOWN"))
