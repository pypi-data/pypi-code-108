from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class UserValidationValidationStatus(Enums.KnownString):
    VALID = "VALID"
    INVALID = "INVALID"
    PARTIALLY_VALID = "PARTIALLY_VALID"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "UserValidationValidationStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of UserValidationValidationStatus must be a string (encountered: {val})")
        newcls = Enum("UserValidationValidationStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(UserValidationValidationStatus, getattr(newcls, "_UNKNOWN"))
