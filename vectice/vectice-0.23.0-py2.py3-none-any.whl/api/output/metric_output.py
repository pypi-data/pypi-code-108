from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import inspect
from vectice.models import metric


@dataclass
class __Output:
    key: str
    value: float
    timestamp: datetime
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, metrics):
        return cls(**{k: v for k, v in metrics.items() if k in inspect.signature(cls).parameters})

    def as_dict(self):
        return asdict(self)


@dataclass
class EntityMetricOutput(metric.Metric, __Output):
    pass
