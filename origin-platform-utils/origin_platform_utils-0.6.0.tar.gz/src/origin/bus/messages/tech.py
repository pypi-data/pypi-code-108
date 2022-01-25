from dataclasses import dataclass

from origin.bus import Message
from origin.models.tech import Technology, TechnologyCodes


@dataclass
class TechnologyUpdate(Message):
    """
    A Technology has been added or updated.
    """
    technology: Technology


@dataclass
class TechnologyRemoved(Message):
    """
    TODO
    """
    codes: TechnologyCodes
