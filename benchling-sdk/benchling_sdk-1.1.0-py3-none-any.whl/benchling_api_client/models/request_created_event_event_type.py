from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestCreatedEventEventType(Enums.KnownString):
    V2_REQUESTCREATED = "v2.request.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestCreatedEventEventType":
        if not isinstance(val, str):
            raise ValueError(f"Value of RequestCreatedEventEventType must be a string (encountered: {val})")
        newcls = Enum("RequestCreatedEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestCreatedEventEventType, getattr(newcls, "_UNKNOWN"))
