from enum import Enum


class StageStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"
    ERROR = "ERROR"

    def __str__(self) -> str:
        return str(self.value)
