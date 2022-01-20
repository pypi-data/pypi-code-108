from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ExternalFileNotePartType(Enums.KnownString):
    EXTERNAL_FILE = "external_file"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ExternalFileNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ExternalFileNotePartType must be a string (encountered: {val})")
        newcls = Enum("ExternalFileNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ExternalFileNotePartType, getattr(newcls, "_UNKNOWN"))
