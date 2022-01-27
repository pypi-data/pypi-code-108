from __future__ import annotations
import asyncio
from kinopoisk.data.id import Id
from kinopoisk.data.name import Name
from kinopoisk.data.poster import Poster
from kinopoisk.data.types import ImageTypes
from dataclasses import dataclass
from dataclasses import field
import kinopoisk.utils as utils


@dataclass(frozen=True)
class BaseMovie:
    """Base class with general methods"""
    
    id : Id = None
    name : Name = None
    poster : Poster = None
    year : int = None
    length : int = None
    countries : list[str] = field(default_factory=list)
    genres : list[str] = field(default_factory=list)


    @staticmethod
    async def _create_from_json(json : dict) -> BaseMovie:
        movie = BaseMovie(
            id=Id(
                json.get('kinopoiskId') if json.get('kinopoiskId') is not None else json.get('filmId'),
                json.get('imdbId')),
            name=Name(original=json.get('nameOriginal'), en=json.get('nameEn'), ru=json.get('nameRu')),
            poster=Poster(json.get('posterUrl'), json.get('posterUrlPreview')),
            year=int(json.get('year')) if json.get('year') is not None else None,
            length=json.get('filmLength') if not isinstance(json.get('filmLength'), str) else sum(await utils.time_to_minute(json.get('filmLength'))),
            countries=([i['country'] for i in json.get('countries')] if json.get('countries') is not None else None),
            genres=([i['genre'] for i in json.get('genres')] if json.get('genres') is not None else None)
            ) 
        return movie


    async def get_all_data(self, client):
        """
        Movie may not have all data, this could be that movie may be take from various API methods, which have different return data details levels.
        @warning: Movie instance changes after call this method to needed movie class e.g. been BaseMovie became Film. 
        
        @param client: Client instance for delegating of methods.
        """

        new_ = await client.get_movie_data(self.id.kinopoisk)
        object.__setattr__(self, '__class__', new_.__class__)
        self.__dict__.update(new_.__dict__)


    async def get_reviews(self, client, page : int=None) -> (list[Review], None):
        """
        Gets reviews of this movie.
        
        @param client: Client instance for delegating of methods.
        """

        return await client.get_reviews(self.id.kinopoisk, page)
    

    async def get_persons(self, client) -> (list[Person], None):
        """
        Gets persons of this movie.
        
        @param client: Client instance for delegating of methods.
        """

        return await client.get_persons_of_movie(self.id.kinopoisk)
    

    async def get_similars(self, client) -> (list[BaseMovie], None):
        """
        Gets persons of this movie.
        
        @param client: Client instance for delegating of methods.
        """

        return await client.get_similars(self.id.kinopoisk)
    

    async def get_images(self, client, type : ImageTypes=ImageTypes.frame, page : int=None) -> (list[BaseMovie], None):
        """
        Gets images of this movie.
        
        @param client: Client instance for delegating of methods.
        """

        return await client.get_images(self.id.kinopoisk, type, page)