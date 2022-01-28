from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class IngredientMeasurementUnits(Enums.KnownString):
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    MG = "mg"
    G = "g"
    UNITS = "Units"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "IngredientMeasurementUnits":
        if not isinstance(val, str):
            raise ValueError(f"Value of IngredientMeasurementUnits must be a string (encountered: {val})")
        newcls = Enum("IngredientMeasurementUnits", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(IngredientMeasurementUnits, getattr(newcls, "_UNKNOWN"))
