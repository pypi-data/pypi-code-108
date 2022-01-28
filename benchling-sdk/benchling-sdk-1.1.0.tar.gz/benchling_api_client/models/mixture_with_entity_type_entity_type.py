from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MixtureWithEntityTypeEntityType(Enums.KnownString):
    MIXTURE = "mixture"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MixtureWithEntityTypeEntityType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of MixtureWithEntityTypeEntityType must be a string (encountered: {val})"
            )
        newcls = Enum("MixtureWithEntityTypeEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MixtureWithEntityTypeEntityType, getattr(newcls, "_UNKNOWN"))
