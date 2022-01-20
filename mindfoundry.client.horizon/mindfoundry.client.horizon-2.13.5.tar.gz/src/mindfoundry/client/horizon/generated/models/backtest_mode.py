from enum import Enum


class BacktestMode(str, Enum):
    TRAINING_DATA = "training_data"
    VALIDATION_DATA = "validation_data"
    ALL_DATA = "all_data"
    CUSTOM_RANGE = "custom_range"

    def __str__(self) -> str:
        return str(self.value)
