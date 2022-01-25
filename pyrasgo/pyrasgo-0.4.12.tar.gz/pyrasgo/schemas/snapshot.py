from dataclasses import dataclass
from pydantic import BaseModel

from datetime import datetime

class Snapshot(BaseModel):
    timestamp: str
    fqtn: str