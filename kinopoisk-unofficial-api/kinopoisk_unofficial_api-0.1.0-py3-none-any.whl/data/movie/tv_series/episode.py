from __future__ import annotations
import asyncio
from kinopoisk.data.name import Name
from kinopoisk.data.description import Description
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime



@dataclass(frozen=True)
class Episode:
    """Simple episode dataclass"""
    season_number : int = None
    number : int = None
    name : Name = None
    description : Description = None
    release_date : datetime = None


    @staticmethod
    async def _create_from_json(json : dict) -> Episode:
        episode = Episode(
            season_number=json.get('seasonNumber'),
            number=json.get('episodeNumber'),
            name=Name(
                ru=json.get('nameRu'),
                en=json.get('nameEn')),
            description=Description(json.get('synopsis'), None),
            release_date=datetime.strptime(json.get('releaseDate'), '%Y-%m-%d') if json.get('releaseDate') is not None else None
        )
        return episode

