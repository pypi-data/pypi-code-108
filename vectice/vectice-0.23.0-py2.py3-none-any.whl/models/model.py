from __future__ import annotations

from dataclasses import dataclass
from vectice.entity.model import ModelType
from typing import Optional


@dataclass
class Model:
    name: str
    type: ModelType
    description: Optional[str] = None

    def with_description(self, description: str):
        """"""
        self.description = description
        return self
