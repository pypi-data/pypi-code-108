from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SchemaLinkFieldDefinitionType(Enums.KnownString):
    ENTITY_LINK = "entity_link"
    ENTRY_LINK = "entry_link"
    PART_LINK = "part_link"
    TRANSLATION_LINK = "translation_link"
    BATCH_LINK = "batch_link"
    STORAGE_LINK = "storage_link"
    ASSAY_REQUEST_LINK = "assay_request_link"
    ASSAY_RESULT_LINK = "assay_result_link"
    ASSAY_RUN_LINK = "assay_run_link"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SchemaLinkFieldDefinitionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SchemaLinkFieldDefinitionType must be a string (encountered: {val})")
        newcls = Enum("SchemaLinkFieldDefinitionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SchemaLinkFieldDefinitionType, getattr(newcls, "_UNKNOWN"))
