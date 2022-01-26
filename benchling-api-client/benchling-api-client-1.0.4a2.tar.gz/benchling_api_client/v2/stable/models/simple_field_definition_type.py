from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SimpleFieldDefinitionType(Enums.KnownString):
    DNA_SEQUENCE_LINK = "dna_sequence_link"
    AA_SEQUENCE_LINK = "aa_sequence_link"
    CUSTOM_ENTITY_LINK = "custom_entity_link"
    MIXTURE_LINK = "mixture_link"
    BLOB_LINK = "blob_link"
    TEXT = "text"
    LONG_TEXT = "long_text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SimpleFieldDefinitionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SimpleFieldDefinitionType must be a string (encountered: {val})")
        newcls = Enum("SimpleFieldDefinitionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SimpleFieldDefinitionType, getattr(newcls, "_UNKNOWN"))
