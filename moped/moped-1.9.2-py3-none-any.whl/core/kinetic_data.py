from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

__all__ = ["KineticData"]


@dataclass
class KineticData:
    km: Dict[str, float] = field(default_factory=dict)
    kcat: Dict[str, float] = field(default_factory=dict)
    vmax: Dict[str, float] = field(default_factory=dict)
