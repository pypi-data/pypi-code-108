from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskGroupExecutionType(Enums.KnownString):
    DIRECT = "DIRECT"
    ENTRY = "ENTRY"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskGroupExecutionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowTaskGroupExecutionType must be a string (encountered: {val})")
        newcls = Enum("WorkflowTaskGroupExecutionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskGroupExecutionType, getattr(newcls, "_UNKNOWN"))
