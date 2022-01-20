from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ContainersArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    EXPENDED = "Expended"
    SHIPPED = "Shipped"
    CONTAMINATED = "Contaminated"
    EXPIRED = "Expired"
    MISSING = "Missing"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ContainersArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of ContainersArchiveReason must be a string (encountered: {val})")
        newcls = Enum("ContainersArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ContainersArchiveReason, getattr(newcls, "_UNKNOWN"))
