from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskUpdatedStatusEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKUPDATEDSTATUS = "v2.workflowTask.updated.status"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskUpdatedStatusEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskUpdatedStatusEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskUpdatedStatusEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskUpdatedStatusEventEventType, getattr(newcls, "_UNKNOWN"))
