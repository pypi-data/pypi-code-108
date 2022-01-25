from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class PlateCreationTableNotePartType(Enums.KnownString):
    PLATE_CREATION_TABLE = "plate_creation_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "PlateCreationTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of PlateCreationTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("PlateCreationTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(PlateCreationTableNotePartType, getattr(newcls, "_UNKNOWN"))
