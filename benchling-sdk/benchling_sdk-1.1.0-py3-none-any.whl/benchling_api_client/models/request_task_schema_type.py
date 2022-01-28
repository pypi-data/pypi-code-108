from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestTaskSchemaType(Enums.KnownString):
    REQUEST_TASK = "request_task"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestTaskSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of RequestTaskSchemaType must be a string (encountered: {val})")
        newcls = Enum("RequestTaskSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestTaskSchemaType, getattr(newcls, "_UNKNOWN"))
