from dataclasses import dataclass
from ..base import BaseMethod


@dataclass
class Wall(BaseMethod):
    access_token: str
    api_version: str = "5.131"

    from .get import get
