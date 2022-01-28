from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskGroupCreatedEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKGROUPCREATED = "v2.workflowTaskGroup.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskGroupCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskGroupCreatedEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskGroupCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskGroupCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
