from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestStatus(Enums.KnownString):
    REQUESTED = "REQUESTED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of RequestStatus must be a string (encountered: {val})")
        newcls = Enum("RequestStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestStatus, getattr(newcls, "_UNKNOWN"))
