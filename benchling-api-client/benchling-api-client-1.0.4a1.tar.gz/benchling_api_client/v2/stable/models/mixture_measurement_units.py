from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MixtureMeasurementUnits(Enums.KnownString):
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    G = "g"
    KG = "kg"
    UNITS = "Units"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MixtureMeasurementUnits":
        if not isinstance(val, str):
            raise ValueError(f"Value of MixtureMeasurementUnits must be a string (encountered: {val})")
        newcls = Enum("MixtureMeasurementUnits", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MixtureMeasurementUnits, getattr(newcls, "_UNKNOWN"))
