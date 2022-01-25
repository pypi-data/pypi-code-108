from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class LocationSchemaType(Enums.KnownString):
    LOCATION = "location"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "LocationSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of LocationSchemaType must be a string (encountered: {val})")
        newcls = Enum("LocationSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(LocationSchemaType, getattr(newcls, "_UNKNOWN"))
