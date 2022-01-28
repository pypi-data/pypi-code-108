from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayResultSchemaType(Enums.KnownString):
    ASSAY_RESULT = "assay_result"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayResultSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AssayResultSchemaType must be a string (encountered: {val})")
        newcls = Enum("AssayResultSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayResultSchemaType, getattr(newcls, "_UNKNOWN"))
