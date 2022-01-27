from __future__ import annotations
import asyncio
from kinopoisk.data.movie.base_movie import BaseMovie
from kinopoisk.data.id import Id
from kinopoisk.data.name import Name
from kinopoisk.data.poster import Poster
from kinopoisk.data.raiting import Raiting, RaitingData
from kinopoisk.data.age_raiting import AgeRaiting
from kinopoisk.data.url import Url
from kinopoisk.data.description import Description
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import kinopoisk.utils as utils


@dataclass(frozen=True)
class Film(BaseMovie):
    """Simple film dataclass"""
    
    id : Id = None
    name : Name = None
    poster : Poster = None
    raiting : Raiting = None
    url : Url = None
    year : int = None
    length : int = None
    slogan : str = None
    description : str = None
    editor_annotation : str = None
    is_tickets_available : bool = None
    prodaction_status : str = None
    age_rating : AgeRaiting = None
    has_imax : bool = None
    has_3d : bool = None
    last_sync : datetime = None
    countries : list[str] = field(default_factory=list)
    genres : list[str] = field(default_factory=list)


    @staticmethod
    async def _create_from_json(json : dict) -> Film:
        film = Film(
            id=Id(
                json.get('kinopoiskId') if json.get('kinopoiskId') is not None else json.get('filmId'),
                json.get('imdbId')),
            name=Name(original=json.get('nameOriginal'), en=json.get('nameEn'), ru=json.get('nameRu')),
            poster=Poster(json.get('posterUrl'), json.get('posterUrlPreview')),
            raiting=Raiting(
                good_review=RaitingData(json.get('ratingGoodReview'), json.get('ratingGoodReviewVoteCount')),
                kinopoisk=RaitingData(json.get('ratingKinopoisk'), json.get('ratingKinopoiskVoteCount')),
                imdb=RaitingData(json.get('ratingImdb'), json.get('ratingImdbVoteCount')),
                film_critics=RaitingData(json.get('ratingFilmCritics'), json.get('ratingFilmCriticsVoteCount')),
                await_=RaitingData(json.get('ratingAwait'), json.get('ratingAwaitCount')), 
                rf_critics=RaitingData(json.get('ratingRfCritics'), json.get('ratingRfCriticsVoteCount'))),
            url=Url(
                json.get('webUrl') if json.get('webUrl') is not None else f'https://www.kinopoisk.ru/film/{json.get("kinopoiskId")}/',
                f'https://www.imdb.com/title/{json.get("imdbId")}/' if json.get("imdbId") is not None else None),
            year=json.get('year'),
            length=json.get('filmLength') if not isinstance(json.get('filmLength'), str) else sum(await utils.time_to_minute(json.get('filmLength'))),
            slogan=json.get('slogan'),
            description=Description(
                json.get('description'),
                json.get('shortDescription')),
            editor_annotation=json.get('editorAnnotation'),
            is_tickets_available=json.get('isTicketsAvailable'),
            prodaction_status=json.get('productionStatus'),
            age_rating=AgeRaiting(
                mpaa=json.get('ratingMpaa'),
                age_limit=int(json.get('ratingAgeLimits')[3:]) if json.get('ratingAgeLimits') is not None else None),
            has_imax=json.get('hasImax'),
            has_3d=json.get('has3D'),
            last_sync=datetime.strptime(json.get('lastSync'), '%Y-%m-%dT%H:%M:%S.%f') if json.get('lastSync') is not None else None,
            countries=([i['country'] for i in json.get('countries')] if json.get('countries') is not None else None),
            genres=([i['genre'] for i in json.get('genres')] if json.get('genres') is not None else None)
            )
        return film
