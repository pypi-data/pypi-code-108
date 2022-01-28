from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AutomationInputGeneratorCompletedV2BetaEventEventType(Enums.KnownString):
    V2_BETAAUTOMATIONINPUTGENERATORCOMPLETED = "v2-beta.automationInputGenerator.completed"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AutomationInputGeneratorCompletedV2BetaEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AutomationInputGeneratorCompletedV2BetaEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("AutomationInputGeneratorCompletedV2BetaEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AutomationInputGeneratorCompletedV2BetaEventEventType, getattr(newcls, "_UNKNOWN"))
