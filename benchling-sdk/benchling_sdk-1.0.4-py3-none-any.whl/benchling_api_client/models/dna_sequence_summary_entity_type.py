from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequenceSummaryEntityType(Enums.KnownString):
    DNA_SEQUENCE = "dna_sequence"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequenceSummaryEntityType":
        if not isinstance(val, str):
            raise ValueError(f"Value of DnaSequenceSummaryEntityType must be a string (encountered: {val})")
        newcls = Enum("DnaSequenceSummaryEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequenceSummaryEntityType, getattr(newcls, "_UNKNOWN"))
