from dataclasses import dataclass


@dataclass(frozen=True)
class AgeRaiting:
    mpaa : str = 'g'
    age_limit : int = 0