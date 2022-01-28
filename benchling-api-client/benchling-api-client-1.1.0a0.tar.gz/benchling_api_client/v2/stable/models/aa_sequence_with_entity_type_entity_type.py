from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AaSequenceWithEntityTypeEntityType(Enums.KnownString):
    AA_SEQUENCE = "aa_sequence"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AaSequenceWithEntityTypeEntityType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AaSequenceWithEntityTypeEntityType must be a string (encountered: {val})"
            )
        newcls = Enum("AaSequenceWithEntityTypeEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AaSequenceWithEntityTypeEntityType, getattr(newcls, "_UNKNOWN"))
