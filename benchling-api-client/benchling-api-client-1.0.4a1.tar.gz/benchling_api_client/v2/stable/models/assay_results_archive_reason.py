from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayResultsArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    ARCHIVED = "Archived"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayResultsArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayResultsArchiveReason must be a string (encountered: {val})")
        newcls = Enum("AssayResultsArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayResultsArchiveReason, getattr(newcls, "_UNKNOWN"))
