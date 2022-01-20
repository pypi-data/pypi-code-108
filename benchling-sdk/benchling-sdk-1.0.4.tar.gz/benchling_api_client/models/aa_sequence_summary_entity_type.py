from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AaSequenceSummaryEntityType(Enums.KnownString):
    AA_SEQUENCE = "aa_sequence"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AaSequenceSummaryEntityType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AaSequenceSummaryEntityType must be a string (encountered: {val})")
        newcls = Enum("AaSequenceSummaryEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AaSequenceSummaryEntityType, getattr(newcls, "_UNKNOWN"))
