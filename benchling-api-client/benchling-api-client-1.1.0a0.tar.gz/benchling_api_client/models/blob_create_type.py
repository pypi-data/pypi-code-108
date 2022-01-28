from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BlobCreateType(Enums.KnownString):
    RAW_FILE = "RAW_FILE"
    VISUALIZATION = "VISUALIZATION"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BlobCreateType":
        if not isinstance(val, str):
            raise ValueError(f"Value of BlobCreateType must be a string (encountered: {val})")
        newcls = Enum("BlobCreateType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BlobCreateType, getattr(newcls, "_UNKNOWN"))
