from enum import Enum


class IngestionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

    def __str__(self) -> str:
        return str(self.value)
