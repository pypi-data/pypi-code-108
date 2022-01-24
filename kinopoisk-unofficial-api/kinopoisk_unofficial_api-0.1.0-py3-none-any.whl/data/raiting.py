from dataclasses import dataclass


@dataclass(frozen=True)
class RaitingData:
    value : float = 0
    count : int = 0


@dataclass(frozen=True)
class Raiting:
    good_review : RaitingData
    kinopoisk : RaitingData
    imdb : RaitingData
    film_critics : RaitingData
    await_ : RaitingData
    rf_critics : RaitingData
