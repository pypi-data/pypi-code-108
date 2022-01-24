from dataclasses import dataclass

from tomlkit import datetime


@dataclass
class Snapshot():
    timestamp: datetime
    fqtn: str 