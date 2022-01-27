from .enums import Key
from dataclasses import dataclass

@dataclass
class ReplayEvent:
    time: int
    frametime: int
    x: float
    y: float
    keys: Key

@dataclass
class Keypress:
    key_down: int
    key_up: int
