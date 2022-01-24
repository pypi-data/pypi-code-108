import enum


class MovieTypes(enum.Enum):
    film = 'FILM'
    video = 'VIDEO'
    tv_series = 'TV_SERIES'
    mini_series = 'MINI_SERIES'
    tv_show = 'TV_SHOW'
    all = 'ALL'


class FactTypes(enum.Enum):
    fact = 'FACT'
    blooper = 'BLOOPER'