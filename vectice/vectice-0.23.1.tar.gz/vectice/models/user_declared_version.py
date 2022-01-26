from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDeclaredVersion:
    name: Optional[str] = None
    """"""
    uri: Optional[str] = None
    """"""
    description: Optional[str] = None
    """"""
