from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RnaOligoWithEntityTypeEntityType(Enums.KnownString):
    RNA_OLIGO = "rna_oligo"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RnaOligoWithEntityTypeEntityType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of RnaOligoWithEntityTypeEntityType must be a string (encountered: {val})"
            )
        newcls = Enum("RnaOligoWithEntityTypeEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RnaOligoWithEntityTypeEntityType, getattr(newcls, "_UNKNOWN"))
