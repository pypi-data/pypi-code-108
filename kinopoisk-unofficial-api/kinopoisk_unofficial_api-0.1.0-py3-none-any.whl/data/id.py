from dataclasses import dataclass


@dataclass(frozen=True)
class Id:
    kinopoisk : int
    imdb : str