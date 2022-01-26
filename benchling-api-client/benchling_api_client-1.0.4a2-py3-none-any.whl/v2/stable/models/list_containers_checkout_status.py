from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListContainersCheckoutStatus(Enums.KnownString):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CHECKED_OUT = "CHECKED_OUT"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListContainersCheckoutStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListContainersCheckoutStatus must be a string (encountered: {val})")
        newcls = Enum("ListContainersCheckoutStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListContainersCheckoutStatus, getattr(newcls, "_UNKNOWN"))
