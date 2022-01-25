from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class OligoNucleotideType(Enums.KnownString):
    DNA = "DNA"
    RNA = "RNA"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "OligoNucleotideType":
        if not isinstance(val, str):
            raise ValueError(f"Value of OligoNucleotideType must be a string (encountered: {val})")
        newcls = Enum("OligoNucleotideType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(OligoNucleotideType, getattr(newcls, "_UNKNOWN"))
