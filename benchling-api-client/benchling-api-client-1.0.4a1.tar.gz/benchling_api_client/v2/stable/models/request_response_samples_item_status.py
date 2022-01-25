from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestResponseSamplesItemStatus(Enums.KnownString):
    COMPLETED = "COMPLETED"
    DISCARDED = "DISCARDED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestResponseSamplesItemStatus":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of RequestResponseSamplesItemStatus must be a string (encountered: {val})"
            )
        newcls = Enum("RequestResponseSamplesItemStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestResponseSamplesItemStatus, getattr(newcls, "_UNKNOWN"))
