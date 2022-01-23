"""
Trochę synchronicznych metod do użycia w konsoli.
"""
__all__ = "get_camps", "get_plebiscite", "get_castles", "get_crew", "apply_for_job"

from ._client import Client
from ._util import synchronize


@synchronize
async def get_camps():
    async with Client() as client:
        return await client.get_camps()


@synchronize
async def get_plebiscite(year: int):
    async with Client() as client:
        return await client.get_plebiscite(year)


@synchronize
async def get_castles():
    async with Client() as client:
        return await client.get_castles()


@synchronize
async def get_crew():
    async with Client() as client:
        return await client.get_crew()


@synchronize
async def apply_for_job():
    async with Client() as client:
        return await client.apply_for_job()
