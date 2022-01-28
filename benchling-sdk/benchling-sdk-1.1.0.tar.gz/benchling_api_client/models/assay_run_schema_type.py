from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunSchemaType(Enums.KnownString):
    ASSAY_RUN = "assay_run"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayRunSchemaType must be a string (encountered: {val})")
        newcls = Enum("AssayRunSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunSchemaType, getattr(newcls, "_UNKNOWN"))
