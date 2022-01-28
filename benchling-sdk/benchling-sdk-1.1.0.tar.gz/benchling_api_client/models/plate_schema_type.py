from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class PlateSchemaType(Enums.KnownString):
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "PlateSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of PlateSchemaType must be a string (encountered: {val})")
        newcls = Enum("PlateSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(PlateSchemaType, getattr(newcls, "_UNKNOWN"))
