from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import inspect
from vectice.models import property


@dataclass
class __Output:
    id: int
    dataSetVersionId: int
    key: str
    value: str
    timestamp: datetime
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, properties):
        return cls(**{k: v for k, v in properties.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)


@dataclass
class EntityPropertyOutput(property.Property, __Output):
    pass
