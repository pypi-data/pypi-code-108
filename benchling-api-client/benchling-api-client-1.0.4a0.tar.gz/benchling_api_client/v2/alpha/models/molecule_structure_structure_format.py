from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MoleculeStructureStructureFormat(Enums.KnownString):
    SMILES = "smiles"
    MOLFILE = "molfile"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MoleculeStructureStructureFormat":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of MoleculeStructureStructureFormat must be a string (encountered: {val})"
            )
        newcls = Enum("MoleculeStructureStructureFormat", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MoleculeStructureStructureFormat, getattr(newcls, "_UNKNOWN"))
