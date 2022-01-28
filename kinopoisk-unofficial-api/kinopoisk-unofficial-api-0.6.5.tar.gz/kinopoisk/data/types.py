import enum


class MovieTypes(enum.Enum):

    def __str__(self):
        return self.value

    film = 'FILM'
    video = 'VIDEO'
    tv_series = 'TV_SERIES'
    mini_series = 'MINI_SERIES'
    tv_show = 'TV_SHOW'
    all = 'ALL'


class FactTypes(enum.Enum):
    
    def __str__(self):
        return self.value

    fact = 'FACT'
    blooper = 'BLOOPER'


class ImageTypes(enum.Enum):

    def __str__(self):
        return self.value


    frame = 'STILL'
    back_stage = 'SHOOTING'
    poster = 'POSTER'
    fan_art = 'FAN_ART'
    promo = 'PROMO'
    concept_art = 'CONCEPT'
    wallpaper = 'WALLPAPER'
    cover = 'COVER'
    screenshot = 'SCREENSHOT'


class TopTypes(enum.Enum):

    def __str__(self):
        return self.value


    best_250 = 'TOP_250_BEST_FILMS'
    popular_100 = 'TOP_100_POPULAR_FILMS'
    future = 'TOP_AWAIT_FILMS'