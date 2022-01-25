from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskSchemaExecutionType(Enums.KnownString):
    DIRECT = "DIRECT"
    ENTRY = "ENTRY"
    FLOWCHART = "FLOWCHART"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskSchemaExecutionType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskSchemaExecutionType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskSchemaExecutionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskSchemaExecutionType, getattr(newcls, "_UNKNOWN"))
