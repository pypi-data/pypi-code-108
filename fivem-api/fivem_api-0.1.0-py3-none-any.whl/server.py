from fivem.player import Player


class Server:
    def __init__(self, hostname, server, players: list[Player], max_players, resources: list[str], vars: list[str], game_type, map_name):
        self.hostname = hostname
        self.server = server
        self.players = players
        self.max_players = max_players
        self.resources = resources
        self.vars = vars
        self.game = Game(game_type, map_name)

    @staticmethod
    def parse(dynamic: dict, info: dict, players: list[Player]):
        return Server(dynamic.get('hostname'), info.get('server'), players, dynamic.get('sv_maxclients'), info.get('resources'), info.get('vars'), dynamic.get('gametype'), dynamic.get('mapname'))


class Game:
    def __init__(self, game_type, map_name):
        self.game_type = game_type
        self.map_name = map_name
