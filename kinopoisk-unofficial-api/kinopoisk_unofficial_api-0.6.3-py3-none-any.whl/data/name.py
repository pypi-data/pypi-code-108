from dataclasses import dataclass


@dataclass(frozen=True)
class Name:
    original : str = None
    en : str = None
    ru : str = None