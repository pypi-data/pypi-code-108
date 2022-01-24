from __future__ import annotations
import asyncio
from .episode import Episode
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime



@dataclass(frozen=True)
class Season:
    """
    Simple season of tv series dataclass. Contains episodes.

    This class can be iterated of episodes.
    """

    number : int = None
    episodes : list[Episode] = field(default_factory=list)


    @staticmethod
    async def _create_from_json(json : dict)-> Season:
        episodes = []
        for episode in json.get('episodes'):
            episodes.append(await Episode._create_from_json(episode))
        season =  Season(
            number=json.get('number'),
            episodes=episodes
        )
        return season


    def __getitem__(self, index):
        return self.episodes[index]
