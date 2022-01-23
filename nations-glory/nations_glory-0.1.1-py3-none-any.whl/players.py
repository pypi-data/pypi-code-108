from re import I
from nations_glory import Servers
from nations_glory.html import Dom

BASE_URL = 'https://nationsglory.fr/profile/'

class Player():

    def __init__(self, name: str, favorite_server: Servers = None, fetch: bool = True):
        self.name: str = name
        self.favorite_server: str = favorite_server
        self.cards: dict = {}

        for server in Servers:
            self.cards[server] = PlayerCard(self, server)

        if fetch:
            self.fetch()

    def __getitem__(self, key):
        return self.cards[key]

    def get_last_connection(self):
        card: PlayerCard = self[self.favorite_server]
        return card.last_connection

    def get_time_played(self):
        card: PlayerCard = self[self.favorite_server]
        return card.time_played

    def get_rank(self):
        card: PlayerCard = self[self.favorite_server]
        return card.rank

    def get_reputation(self):
        card: PlayerCard = self[self.favorite_server]
        return card.reputation

    def get_country(self):
        card: PlayerCard = self[self.favorite_server]
        return card.country

    def get_country_rank(self):
        card: PlayerCard = self[self.favorite_server]
        return card.country_rank

    def get_power(self):
        card: PlayerCard = self[self.favorite_server]
        return card.power
    
    def get_max_power(self):
        card: PlayerCard = self[self.favorite_server]
        return card.max_power

    last_connection = property(get_last_connection)
    time_played = property(get_time_played)
    rank = property(get_rank)
    reputation = property(get_reputation)
    country = property(get_country)
    country_rank = property(get_country_rank)
    power = property(get_power)
    max_power = property(get_max_power)

    def fetch(self):
        dom = Dom.from_url(BASE_URL + self.name)
        
        for server in Servers:
            card: PlayerCard = self[server]
            card.feed(dom)
    
class PlayerCard(object):
    
    def __init__(self, player: Player, server: Servers):
        self.player = player
        self.server = server

    def feed(self, dom: Dom):
        self.card = dom.find(
            tag='div', 
            classes=['card', 'server-tab'], 
            attributes={'data-server': self.server.value}
        )

        self.last_connection = self.get('dernière connexion')
        self.time_played = self.get('temps de jeu')
        self.rank = self.get('grade')
        self.reputation = self.get('réputation')
        self.country = self.get('pays')
        self.country_rank = self.get('rang de pays')
        power = self.get('power')
        self.power = int(power.split('/')[0]) if power != None else None
        self.max_power = int(power.split('/')[1]) if power != None else None

    def get(self, key: str) -> str:
        label = self.card.find(tag='h4', innerMatch=('^' + key + '$', I))
        if label == None:
            return None
        value = label.parent.find(tag='p')
        link = value.find(tag='a')
        span = value.find(tag='span', classes=[])
        return (link if link != None else span if span != None else value).innerHTML
        