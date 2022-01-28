from abc import ABC
from dataclasses import dataclass


@dataclass
class SequenceFrame(ABC):
    frame_id: str
    relative_timestamp: int
