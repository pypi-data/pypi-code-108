from enum import Enum
from re import I, finditer, search

class Units(Enum):
    YEAR = { 
        'ms': 365.25 * 24 * 3600 * 1000,
        'en': { 'short': 'y', 'singular': 'year', 'plural': 'years' }, 
        'fr': { 'short': 'a', 'singular': 'année', 'plural': 'ans' } 
    }
    MONTH = { 
        'ms': 28 * 24 * 3600 * 1000,
        'en': { 'short': 'mo', 'singular': 'month', 'plural': 'months' },
        'fr': { 'short': 'mo', 'singular': 'mois', 'plural': 'mois' } 
    }
    WEEK = {
        'ms': 7 * 24 * 3600 * 1000,
        'en': { 'short': 'w', 'singular': 'week', 'plural': 'weeks' },
        'fr': { 'short': 'se', 'singular': 'semaine', 'plural': 'semaines' } 
    }
    DAY = {
        'ms': 24 * 3600 * 1000,
        'en': { 'short': 'd', 'singular': 'day', 'plural': 'days' }, 
        'fr': { 'short': 'j', 'singular': 'jour', 'plural': 'jours' } 
    }
    HOUR = {
        'ms': 3600 * 1000,
        'en': { 'short': 'h', 'singular': 'hour', 'plural': 'hours' }, 
        'fr': { 'short': 'h', 'singular': 'heure', 'plural': 'heures' } 
    }
    MINUTE = {
        'ms': 60 * 1000,
        'en': { 'short': 'm', 'singular': 'minute', 'plural': 'minutes' }, 
        'fr': { 'short': 'm', 'singular': 'minute', 'plural': 'minutes' } 
    }
    SECOND = {
        'ms': 1000,
        'en': { 'short': 's', 'singular': 'second', 'plural': 'seconds' }, 
        'fr': { 'short': 's', 'singular': 'seconde', 'plural': 'secondes' } 
    }
    MILLISECOND = {
        'ms': 1,
        'en': { 'short': 'ms', 'singular': 'millisecond', 'plural': 'milliseconds' }, 
        'fr': { 'short': 'ms', 'singular': 'milliseconde', 'plural': 'millisecondes' } 
    }

    def get(string: str):
        for unit in Units:
            value = unit.value
            if (
                value['en']['short'] == string.casefold() or
                value['en']['singular'] == string.casefold() or
                value['en']['plural'] == string.casefold() or
                value['fr']['short'] == string.casefold() or
                value['fr']['singular'] == string.casefold() or
                value['fr']['plural'] == string.casefold()
            ):
                return unit
        print("Couldn't recognize unit " + string)
        return None

def parse_duration(string: str):
    duration: int = 0
    for match in finditer("\d+ ?[a-zé]+", string, I):
        number = int(search("\d+", match.group()).group())
        unit = Units.get(search("[a-zé]+", match.group(), I).group())
        duration += (number * unit.value['ms']) if unit != None else 0
    return int(duration)
        