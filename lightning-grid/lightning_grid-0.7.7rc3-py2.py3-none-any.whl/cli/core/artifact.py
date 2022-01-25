from dataclasses import dataclass


@dataclass
class Artifact:
    url: str
    path: str
    filename: str
