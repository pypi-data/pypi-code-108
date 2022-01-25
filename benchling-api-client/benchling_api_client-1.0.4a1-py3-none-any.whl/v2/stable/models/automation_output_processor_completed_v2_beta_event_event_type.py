from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AutomationOutputProcessorCompletedV2BetaEventEventType(Enums.KnownString):
    V2_BETAAUTOMATIONOUTPUTPROCESSORCOMPLETED = "v2-beta.automationOutputProcessor.completed"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AutomationOutputProcessorCompletedV2BetaEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AutomationOutputProcessorCompletedV2BetaEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("AutomationOutputProcessorCompletedV2BetaEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AutomationOutputProcessorCompletedV2BetaEventEventType, getattr(newcls, "_UNKNOWN"))
