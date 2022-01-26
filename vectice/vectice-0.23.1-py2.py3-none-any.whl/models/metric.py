from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Metric:
    key: str
    """"""
    value: float
    """"""
    timestamp: datetime = field(default_factory=datetime.now)
    """"""
    name: Optional[str] = None
    """"""
