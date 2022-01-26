from enum import Enum


class JobStatus(str, Enum):
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
