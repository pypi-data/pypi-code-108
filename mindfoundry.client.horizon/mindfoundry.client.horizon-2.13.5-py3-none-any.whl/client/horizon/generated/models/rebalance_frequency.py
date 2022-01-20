from enum import Enum


class RebalanceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        return str(self.value)
