from enum import Enum


class PrinterActivityState(Enum):
    STOPPED = 'STOPPED'
    READY = 'READY'
    RUNNING = 'RUNNING'
