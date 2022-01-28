from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunNotePartType(Enums.KnownString):
    ASSAY_RUN = "assay_run"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayRunNotePartType must be a string (encountered: {val})")
        newcls = Enum("AssayRunNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunNotePartType, getattr(newcls, "_UNKNOWN"))
