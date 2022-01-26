from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestSchemaType(Enums.KnownString):
    REQUEST = "request"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of RequestSchemaType must be a string (encountered: {val})")
        newcls = Enum("RequestSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestSchemaType, getattr(newcls, "_UNKNOWN"))
