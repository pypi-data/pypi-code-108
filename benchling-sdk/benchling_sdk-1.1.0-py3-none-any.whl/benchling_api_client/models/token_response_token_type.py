from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TokenResponseTokenType(Enums.KnownString):
    BEARER = "Bearer"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TokenResponseTokenType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TokenResponseTokenType must be a string (encountered: {val})")
        newcls = Enum("TokenResponseTokenType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TokenResponseTokenType, getattr(newcls, "_UNKNOWN"))
