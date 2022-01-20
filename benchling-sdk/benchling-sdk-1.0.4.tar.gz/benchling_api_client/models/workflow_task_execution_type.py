from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskExecutionType(Enums.KnownString):
    DIRECT = "DIRECT"
    ENTRY = "ENTRY"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskExecutionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowTaskExecutionType must be a string (encountered: {val})")
        newcls = Enum("WorkflowTaskExecutionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskExecutionType, getattr(newcls, "_UNKNOWN"))
