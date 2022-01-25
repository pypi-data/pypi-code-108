from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BadRequestErrorErrorType(Enums.KnownString):
    INVALID_REQUEST_ERROR = "invalid_request_error"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BadRequestErrorErrorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of BadRequestErrorErrorType must be a string (encountered: {val})")
        newcls = Enum("BadRequestErrorErrorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BadRequestErrorErrorType, getattr(newcls, "_UNKNOWN"))
