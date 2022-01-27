from dataclasses import dataclass


@dataclass(frozen=True)
class Poster:
    big : str
    small : str