from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Property:
    key: str
    """"""
    value: str
    """"""
    timestamp: datetime = field(default_factory=datetime.now)
    """"""
    name: Optional[str] = None
    """"""
