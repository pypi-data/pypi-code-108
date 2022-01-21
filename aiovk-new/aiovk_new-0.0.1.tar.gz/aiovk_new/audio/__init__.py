from dataclasses import dataclass
from ..base import BaseMethod


@dataclass
class Audio(BaseMethod):
    access_token: str
    api_version: str = "5.131"

    from .search import search
    from .get import get
