from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AaSequencesMatchBasesArchiveReason(Enums.KnownString):
    NOT_ARCHIVED = "NOT_ARCHIVED"
    OTHER = "Other"
    ARCHIVED = "Archived"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AaSequencesMatchBasesArchiveReason":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AaSequencesMatchBasesArchiveReason must be a string (encountered: {val})"
            )
        newcls = Enum("AaSequencesMatchBasesArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AaSequencesMatchBasesArchiveReason, getattr(newcls, "_UNKNOWN"))
