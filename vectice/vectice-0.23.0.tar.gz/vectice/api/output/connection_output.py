from dataclasses import dataclass


@dataclass
class __Output:
    id: int
    name: str
    status: str
    type: str


@dataclass
class ConnectionOutput(__Output):
    pass
