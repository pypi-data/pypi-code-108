"""This module defines the groups in Qtile"""

from enum import Enum
from libqtile.config import Group


class GroupName(Enum):
    """Enumerated group names"""

    WEB = "WEB"
    CHAT = "CHAT"
    TERM = "TERM"
    DEV = "DEV"
    NULL = "NULL"
    TMP = "TMP"
    CALL = "CALL"


groups = [Group(f"{ix+1}: {group.value}") for ix, group in enumerate(list(GroupName))]
