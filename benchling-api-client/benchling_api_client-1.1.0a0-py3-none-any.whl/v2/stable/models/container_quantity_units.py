from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ContainerQuantityUnits(Enums.KnownString):
    L = "L"
    ML = "mL"
    UL = "uL"
    NL = "nL"
    PL = "pL"
    GAL_US = "gal (US)"
    QT_US = "qt (US)"
    PT_US = "pt (US)"
    KG = "kg"
    G = "g"
    MG = "mg"
    UG = "ug"
    NG = "ng"
    PG = "pg"
    LB = "lb"
    OZ = "oz"
    MOL = "mol"
    MMOL = "mmol"
    UMOL = "umol"
    NMOL = "nmol"
    PMOL = "pmol"
    CELLS = "cells"
    VALUE_22 = "(x10^6) cells"
    VALUE_23 = "(x10^9) cells"
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
