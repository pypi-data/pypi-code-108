from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AsyncTaskStatus(Enums.KnownString):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AsyncTaskStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of AsyncTaskStatus must be a string (encountered: {val})")
        newcls = Enum("AsyncTaskStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AsyncTaskStatus, getattr(newcls, "_UNKNOWN"))
