from enum import Enum


class RebalanceWeeklyDay(str, Enum):
    NA = "na"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"

    def __str__(self) -> str:
        return str(self.value)
