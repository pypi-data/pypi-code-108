from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequencesMatchBasesArchiveReason(Enums.KnownString):
    NOT_ARCHIVED = "NOT_ARCHIVED"
    OTHER = "Other"
    ARCHIVED = "Archived"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequencesMatchBasesArchiveReason":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of DnaSequencesMatchBasesArchiveReason must be a string (encountered: {val})"
            )
        newcls = Enum("DnaSequencesMatchBasesArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequencesMatchBasesArchiveReason, getattr(newcls, "_UNKNOWN"))
