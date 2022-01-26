from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Dataset:
    name: str
    description: Optional[str] = None

    def with_description(self, description: str):
        """ """
        self.description = description
        return self
