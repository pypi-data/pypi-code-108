from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MixturePrepTableNotePartType(Enums.KnownString):
    MIXTURE_PREP_TABLE = "mixture_prep_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MixturePrepTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of MixturePrepTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("MixturePrepTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MixturePrepTableNotePartType, getattr(newcls, "_UNKNOWN"))
