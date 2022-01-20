from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TokenCreateGrantType(Enums.KnownString):
    CLIENT_CREDENTIALS = "client_credentials"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TokenCreateGrantType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TokenCreateGrantType must be a string (encountered: {val})")
        newcls = Enum("TokenCreateGrantType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TokenCreateGrantType, getattr(newcls, "_UNKNOWN"))
