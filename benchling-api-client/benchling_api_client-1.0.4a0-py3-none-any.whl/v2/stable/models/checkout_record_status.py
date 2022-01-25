from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class CheckoutRecordStatus(Enums.KnownString):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CHECKED_OUT = "CHECKED_OUT"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "CheckoutRecordStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of CheckoutRecordStatus must be a string (encountered: {val})")
        newcls = Enum("CheckoutRecordStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(CheckoutRecordStatus, getattr(newcls, "_UNKNOWN"))
