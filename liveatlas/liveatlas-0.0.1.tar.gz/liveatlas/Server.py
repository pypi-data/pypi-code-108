"""

"""
import requests

from DateAndTime import DateAndTime
from Player import Player
from Town import Town


def make_request(map_url):
    """
    Makes a request to the server for data and then converts it into JSON

    :param map_url: Request-compatible URL. NOT the URL of the map itself. See answer from usr7606063 on this post
                    for instructions on how to get a properly formatted URL:
                    https://stackoverflow.com/questions/42397767/python-scraping-of-dynamic-content-visual-different-from-html-source-code
    :return: json object response from server
    """
    return requests.get(map_url).json()


class Server:
    def __init__(self, map_url):
        """
        
        """
        self.data = make_request(map_url)
        self.players = self.read_players_from_json()
        pass

    def read_players_from_json(self):
        """
        Parses JSON data and finds the players list, then constructs Player objects containing their name, coordinates,
        and if they are visible on the map.
        :param data: json object returned by make_request(map_url)
        :return: list of Player objects
        """
        players_data = self.data['players']
        players = []
        for pD in players_data:
            visible = True if pD['world'] == 'world' else False
            player = Player(pD['account'], pD['x'], pD['y'], pD['z'], visible)
            players.append(player)
        return players

    def read_date_and_time_from_json(self):
        """
        Parses JSON data and constructs a DateAndTime object from the timestamp and game time
        :param data: json object returned by make_request(map_url)
        :return: DateAndTime object
        """
        game_time = self.data['servertime']
        timestamp = self.data['timestamp']
        return DateAndTime(timestamp, game_time)

    def read_town_and_camp_data_from_json(self):
        updates = self.data['updates']
        towns = []
        camps = []
        for u in updates:
            if "msg" in u and u["msg"] == "markerupdated":
                if "icon" in u and u['icon'] == "townycamps.camp":
                    # todo: make this create a camp object & append to camps[]
                    pass
                elif u['id'].endswith('__home'):
                    # means this markerupdated is a town
                    towns.append(Town(u['desc']))
                else:
                    print("Non-town/Camp markers exist! id: " + u['id'])

        towns_and_camps = [towns, camps]
        return towns_and_camps


