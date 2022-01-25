from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskExecutionOriginType(Enums.KnownString):
    API = "API"
    ENTRY = "ENTRY"
    MODAL = "MODAL"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskExecutionOriginType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskExecutionOriginType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskExecutionOriginType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskExecutionOriginType, getattr(newcls, "_UNKNOWN"))
