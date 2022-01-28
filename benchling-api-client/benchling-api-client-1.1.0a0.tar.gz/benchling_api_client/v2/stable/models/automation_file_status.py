from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AutomationFileStatus(Enums.KnownString):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AutomationFileStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of AutomationFileStatus must be a string (encountered: {val})")
        newcls = Enum("AutomationFileStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AutomationFileStatus, getattr(newcls, "_UNKNOWN"))
