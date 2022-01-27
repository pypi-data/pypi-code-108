import json
import aiohttp

from fivem.player import Player
from fivem.server import Server


class FiveM:
    """Base class for a FiveM server"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def get_server(self) -> Server:
        dynamic = await self.get_dynamic_raw()

        info = await self.get_info_raw()
        players = list[Player]()
        if (dynamic['clients'] > 0):
            players = await self.get_players()

        return Server.parse(dynamic, info, players)

    async def get_players(self) -> list[Player]:
        players = list()
        for rawPlayer in await self.get_players_raw():
            players.append(Player(rawPlayer))
        return players

    async def get_dynamic_raw(self) -> dict:
        return await self.make_request('dynamic.json')

    async def get_info_raw(self) -> dict:
        return await self.make_request('info.json')

    async def get_players_raw(self) -> list[dict]:
        return await self.make_request('players.json')

    async def make_request(self, uri):
        base = 'http://{}:{}/{}'
        url = base.format(self.host, self.port, uri)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.text()
                    return json.loads(data)
            except aiohttp.ClientConnectorError as e:
                raise FiveMServerOfflineError


class FiveMServerOfflineError(Exception):
    pass
