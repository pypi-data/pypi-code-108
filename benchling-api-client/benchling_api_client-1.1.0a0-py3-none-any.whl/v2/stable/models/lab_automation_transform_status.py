from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class LabAutomationTransformStatus(Enums.KnownString):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "LabAutomationTransformStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of LabAutomationTransformStatus must be a string (encountered: {val})")
        newcls = Enum("LabAutomationTransformStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(LabAutomationTransformStatus, getattr(newcls, "_UNKNOWN"))
