from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class NotFoundErrorErrorType(Enums.KnownString):
    INVALID_REQUEST_ERROR = "invalid_request_error"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "NotFoundErrorErrorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of NotFoundErrorErrorType must be a string (encountered: {val})")
        newcls = Enum("NotFoundErrorErrorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(NotFoundErrorErrorType, getattr(newcls, "_UNKNOWN"))
