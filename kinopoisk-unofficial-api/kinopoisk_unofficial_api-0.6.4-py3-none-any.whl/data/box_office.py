from __future__ import annotations
import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime



@dataclass(frozen=True)
class BoxOffice:
    world : int = None
    budget : int = None
    marketing : int = None
    usa : int = None
    type : str = 'USD'


    @staticmethod
    async def _create_from_json(json : dict)-> BoxOffice:
        world = None
        budget = None
        marketing = None
        usa = None
        type = 'USD'
        for item in json.get('items'):
            if item.get('type') == 'WORLD':
                world = item.get('amount')
                type = item.get('currencyCode')
            elif item.get('type') == 'BUDGET':
                budget = item.get('amount')
            elif item.get('type') == 'MARKETING':
                marketing = item.get('amount')
            elif item.get('type') == 'USA':
                usa = item.get('amount')


        box_office = BoxOffice(
            world=world,
            budget=budget,
            marketing=marketing,
            usa=usa,
            type=type
            )
        return box_office
    
