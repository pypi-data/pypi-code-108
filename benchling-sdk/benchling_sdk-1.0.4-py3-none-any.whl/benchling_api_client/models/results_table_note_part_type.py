from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ResultsTableNotePartType(Enums.KnownString):
    RESULTS_TABLE = "results_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ResultsTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ResultsTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("ResultsTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ResultsTableNotePartType, getattr(newcls, "_UNKNOWN"))
