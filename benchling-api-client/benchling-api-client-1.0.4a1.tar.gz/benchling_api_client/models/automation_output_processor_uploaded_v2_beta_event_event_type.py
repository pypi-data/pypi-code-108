from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AutomationOutputProcessorUploadedV2BetaEventEventType(Enums.KnownString):
    V2_BETAAUTOMATIONOUTPUTPROCESSORUPLOADED = "v2-beta.automationOutputProcessor.uploaded"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AutomationOutputProcessorUploadedV2BetaEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AutomationOutputProcessorUploadedV2BetaEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("AutomationOutputProcessorUploadedV2BetaEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AutomationOutputProcessorUploadedV2BetaEventEventType, getattr(newcls, "_UNKNOWN"))
