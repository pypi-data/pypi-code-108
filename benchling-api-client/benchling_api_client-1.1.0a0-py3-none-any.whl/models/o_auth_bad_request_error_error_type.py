from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class OAuthBadRequestErrorErrorType(Enums.KnownString):
    INVALID_REQUEST = "invalid_request"
    INVALID_GRANT = "invalid_grant"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "OAuthBadRequestErrorErrorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of OAuthBadRequestErrorErrorType must be a string (encountered: {val})")
        newcls = Enum("OAuthBadRequestErrorErrorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(OAuthBadRequestErrorErrorType, getattr(newcls, "_UNKNOWN"))
