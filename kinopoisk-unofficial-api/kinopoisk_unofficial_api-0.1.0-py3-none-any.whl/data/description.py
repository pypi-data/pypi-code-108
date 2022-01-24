from dataclasses import dataclass


@dataclass(frozen=True)
class Description:
    long : str
    short : str