from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaOligoWithEntityTypeEntityType(Enums.KnownString):
    DNA_OLIGO = "dna_oligo"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaOligoWithEntityTypeEntityType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of DnaOligoWithEntityTypeEntityType must be a string (encountered: {val})"
            )
        newcls = Enum("DnaOligoWithEntityTypeEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaOligoWithEntityTypeEntityType, getattr(newcls, "_UNKNOWN"))
