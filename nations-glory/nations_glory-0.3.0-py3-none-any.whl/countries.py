from nations_glory import Servers
from nations_glory.html import Element
from enum import Enum
import json as JSON
import requests as https
from html_to_json import convert as html_to_json

MARKERS_PATH="/tiles/_markers_/marker_world.json"
AREA_SUFFIX="__world__0"

class CountryRanks(Enum):
    LEADER  = 'leader'
    OFFICIER = 'officier'
    MEMBER = 'membre'
    RECRUIT = 'recrue'
    CUSTOM = 'custom'
    NONE = 'pas de rang'

    def get(key: str):
        if key == None:
            return CountryRanks.NONE
        for rank in CountryRanks:
            if rank.value == key.casefold():
                return rank
        return CountryRanks.CUSTOM

class Country():
    def __init__(self, name: str, server: Servers, fetch: bool = True):
        self.name = name
        self.server = server
        self.card = CountryCard(self)

        if fetch:
            self.fetch()

    def fetch(self):
        json = https.get(self.server.get_map_url() + MARKERS_PATH).text
        dict = JSON.loads(json)
        self.card.feed(dict)
        return self

    def get_description(self):
        return self.card.description

    def get_claims(self):
        return self.card.claims

    def get_power(self):
        return self.card.power

    def get_max_power(self):
        return self.card.max_power

    def get_mmr(self):
        return self.card.mmr

    def get_leader(self):
        return self.card.leader

    def get_members(self):
        return self.card.members

    description: str = property(get_description)
    claims: int = property(get_claims)
    power: int = property(get_power)
    max_power: int = property(get_max_power)
    mmr: int = property(get_mmr)
    leader: str = property(get_leader)
    members: list[str] = property(get_members)

class CountryCard(object):
    
    def __init__(self, country: Country):
        self.country = country
        self.card = Element()

    def feed(self, dict: dict):
        html = dict['sets']['factions.markerset']['areas'][self.country.name + AREA_SUFFIX]['desc']
        dict = html_to_json(html)
        self.card.feed(None, 'div', dict)

        spans: list[Element] = self.card.findAll(tag='span')
        self.created_at = spans[1].innerHTML
        self.description = spans[2].innerHTML
        
        stats = spans[3].innerHTML.split('\n')
        self.claims = int(stats[0])
        self.mmr = int(stats[2])

        power = stats[1].split(' / ')
        self.power = int(power[0])
        self.max_power = int(power[1])

        div = self.card.find(tag='div', classes=['infowindow'])
        leader_members = div.innerHTML.split('\n')
        self.leader = leader_members[0]
        self.members = leader_members[1].split(', ')
               