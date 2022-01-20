from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequenceWithEntityTypeEntityType(Enums.KnownString):
    DNA_SEQUENCE = "dna_sequence"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequenceWithEntityTypeEntityType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of DnaSequenceWithEntityTypeEntityType must be a string (encountered: {val})"
            )
        newcls = Enum("DnaSequenceWithEntityTypeEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequenceWithEntityTypeEntityType, getattr(newcls, "_UNKNOWN"))
