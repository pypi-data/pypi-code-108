from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntriesArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntriesArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntriesArchiveReason must be a string (encountered: {val})")
        newcls = Enum("EntriesArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntriesArchiveReason, getattr(newcls, "_UNKNOWN"))
