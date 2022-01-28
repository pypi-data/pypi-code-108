import datetime
from dataclasses import dataclass
from typing import Dict

BASE_URL = "https://api.arcanebin.com"
MAX_SIZE = {
    "name": 200,
    "description": 2500,
    "code": 15000,
    "error": 5000,
}


@dataclass
class Entry:
    uuid: str = None
    code: str = None
    error: str = None
    name: str = None
    description: str = None
    created_by: Dict = None
    created_at: datetime.datetime = None

    def resolve_url(self):
        return BASE_URL + "/view/" + self.uuid
