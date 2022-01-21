from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set

__all__ = ["Monomer"]


@dataclass
class Monomer:
    id: str
    sequence: str | None
    database_links: Dict[str, Set[str]] = field(default_factory=dict)
