from enum import Enum

class RoxState(Enum):
    Idle = 1,
    SettingUp = 2,
    Set = 3,
    ShuttingDown = 4,
    Corrupted = 5