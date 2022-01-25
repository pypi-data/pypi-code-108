from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntryLinkType(Enums.KnownString):
    LINK = "link"
    USER = "user"
    REQUEST = "request"
    ENTRY = "entry"
    STAGE_ENTRY = "stage_entry"
    PROTOCOL = "protocol"
    WORKFLOW = "workflow"
    CUSTOM_ENTITY = "custom_entity"
    AA_SEQUENCE = "aa_sequence"
    DNA_SEQUENCE = "dna_sequence"
    BATCH = "batch"
    BOX = "box"
    CONTAINER = "container"
    LOCATION = "location"
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntryLinkType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntryLinkType must be a string (encountered: {val})")
        newcls = Enum("EntryLinkType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntryLinkType, getattr(newcls, "_UNKNOWN"))
