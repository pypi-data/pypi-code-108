from dataclasses import dataclass


@dataclass(frozen=True)
class Url:
    kinopoisk : str
    imdb : str
