from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ContainerQuantityUnits(Enums.KnownString):
    PL = "pL"
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    PG = "pg"
    NG = "ng"
    UG = "ug"
    MG = "mg"
    G = "g"
    KG = "kg"
    ITEMS = "items"
    UNITS = "units"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ContainerQuantityUnits":
        if not isinstance(val, str):
            raise ValueError(f"Value of ContainerQuantityUnits must be a string (encountered: {val})")
        newcls = Enum("ContainerQuantityUnits", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ContainerQuantityUnits, getattr(newcls, "_UNKNOWN"))
