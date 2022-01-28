from __future__ import annotations
import asyncio
from dataclasses import dataclass



@dataclass(frozen=True)
class Blooper:
    text : str = None
    is_spoiler : bool = None


    @staticmethod
    async def _create_from_json(json : dict)-> Blooper:
        blooper = Blooper(
            text=json.get('text'),
            is_spoiler=False)
        return blooper

