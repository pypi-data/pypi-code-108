from enum import Enum


class StationarisationStrategy(str, Enum):
    KEEP_FAIL = "keep_fail"
    DISCARD_FAIL = "discard_fail"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
