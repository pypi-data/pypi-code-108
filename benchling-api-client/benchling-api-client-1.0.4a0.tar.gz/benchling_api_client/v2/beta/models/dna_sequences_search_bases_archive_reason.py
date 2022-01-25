from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequencesSearchBasesArchiveReason(Enums.KnownString):
    NOT_ARCHIVED = "NOT_ARCHIVED"
    OTHER = "Other"
    ARCHIVED = "Archived"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequencesSearchBasesArchiveReason":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of DnaSequencesSearchBasesArchiveReason must be a string (encountered: {val})"
            )
        newcls = Enum("DnaSequencesSearchBasesArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequencesSearchBasesArchiveReason, getattr(newcls, "_UNKNOWN"))
