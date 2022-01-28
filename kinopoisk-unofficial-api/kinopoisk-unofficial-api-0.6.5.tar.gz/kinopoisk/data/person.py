from __future__ import annotations
import asyncio
# from .data import *
from kinopoisk.data.id import *
from kinopoisk.data.name import *
from kinopoisk.data.poster import *
from kinopoisk.data.fact import *
from kinopoisk.data.movie import Film, TVSeries
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


@dataclass(frozen=True)
class Person:
    """Simple person dataclass"""
    id : Id = None
    name : Name = None
    character : str = None
    photo : Poster = None
    is_actor : bool = None
    is_director : bool = None
    is_writer : bool = None
    is_editor : bool = None

    is_male : bool = None
    growth : int = None
    birthday : datetime = None
    death : datetime = None
    age : int = None
    birthplace : str = None
    deathplace : str = None
    has_awards : int = None
    professions : list[str] = field(default_factory=list)
    facts : list[Fact] = field(default_factory=list)
    films : list[tuple] = field(default_factory=list)


    @staticmethod
    async def _create_from_json(json : dict) -> Film:
        person = Person(
            id=Id(
                kinopoisk=json.get('personId') if json.get('personId') is not None else json.get('staffId') if json.get('staffId') is not None else json.get('kinopoiskId'),
                imdb=None
            ),
            name=Name(
                ru=json.get('nameRu'),
                en=json.get('nameEn')
            ),
            character=json.get('description'),
            photo=Poster(
                json.get('posterUrl'),
                None
            ),
            is_director= True if json.get('professionKey') == 'DIRECTOR' else False,
            is_actor= True if json.get('professionKey') == 'ACTOR' else False,
            is_writer= True if json.get('professionKey') == 'WRITER' else False,
            is_editor= True if json.get('professionKey') == 'EDITOR' else False,

            is_male= True if json.get('sex') == 'MALE' else False if json.get('sex') == 'FEMALE' else None,
            growth=json.get('growth'),
            birthday=datetime.strptime(json.get('birthday'), '%Y-%m-%d') if json.get('birthday') is not None else None,
            death=datetime.strptime(json.get('death'), '%Y-%m-%d') if json.get('death') is not None else None,
            age=json.get('age'),
            birthplace=json.get('birthplace'),
            deathplace=json.get('deathplace'),
            has_awards=json.get('hasAwards'),
            professions=json.get('profession').split(',') if json.get('profession') is not None else None,
            facts=[Film(i) for i in json.get('facts')] if json.get('facts') is not None else None,
            films=[(await Film._create_from_json(i), {'character': i.get('description')}) for i in json.get('films')] if json.get('films') is not None else None
        )
        return person


    async def get_all_data(self, client):
        """
        Person may not have all data, this could be that person may be take from various API methods, which have different return data details levels.
        
        @param client: Client instance for delegating of methods.
        """
        new_ = await client.get_person_data(self.id.kinopoisk)
        self.__dict__.update(new_.__dict__)
