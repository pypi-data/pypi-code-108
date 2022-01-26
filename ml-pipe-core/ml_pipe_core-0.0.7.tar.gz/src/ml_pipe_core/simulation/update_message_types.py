import dataclasses
from typing import List

from ..message import Message


@dataclasses.dataclass
class UpdateMessage(Message):
    source: str
    updated: List[str]


@dataclasses.dataclass
class SetMachineMessage(Message):
    data: dict
