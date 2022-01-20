from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DeprecatedContainerVolumeForInputUnits(Enums.KnownString):
    PL = "pL"
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DeprecatedContainerVolumeForInputUnits":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of DeprecatedContainerVolumeForInputUnits must be a string (encountered: {val})"
            )
        newcls = Enum("DeprecatedContainerVolumeForInputUnits", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DeprecatedContainerVolumeForInputUnits, getattr(newcls, "_UNKNOWN"))
