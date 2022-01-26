from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AutomationOutputProcessorsArchiveReason(Enums.KnownString):
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
    def of_unknown(val: str) -> "AutomationOutputProcessorsArchiveReason":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AutomationOutputProcessorsArchiveReason must be a string (encountered: {val})"
            )
        newcls = Enum("AutomationOutputProcessorsArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AutomationOutputProcessorsArchiveReason, getattr(newcls, "_UNKNOWN"))
