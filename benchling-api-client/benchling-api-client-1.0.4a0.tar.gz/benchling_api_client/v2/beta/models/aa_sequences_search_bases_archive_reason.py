from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AaSequencesSearchBasesArchiveReason(Enums.KnownString):
    NOT_ARCHIVED = "NOT_ARCHIVED"
    OTHER = "Other"
    ARCHIVED = "Archived"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AaSequencesSearchBasesArchiveReason":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AaSequencesSearchBasesArchiveReason must be a string (encountered: {val})"
            )
        newcls = Enum("AaSequencesSearchBasesArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AaSequencesSearchBasesArchiveReason, getattr(newcls, "_UNKNOWN"))
