from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskCreatedEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKCREATED = "v2.workflowTask.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskCreatedEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
