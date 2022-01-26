from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class PlateType(Enums.KnownString):
    MATRIX_PLATE = "matrix_plate"
    WELL_PLATE = "well_plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "PlateType":
        if not isinstance(val, str):
            raise ValueError(f"Value of PlateType must be a string (encountered: {val})")
        newcls = Enum("PlateType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(PlateType, getattr(newcls, "_UNKNOWN"))
