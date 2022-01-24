from nations_glory import Servers
from enum import Enum

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
    def __init__(self, name: str, server: Servers):
        self.name = name