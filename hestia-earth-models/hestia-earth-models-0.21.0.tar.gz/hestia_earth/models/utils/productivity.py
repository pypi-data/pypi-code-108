from enum import Enum
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.utils.term import get_lookup_value


class PRODUCTIVITY(Enum):
    HIGH = 'high'
    LOW = 'low'


HIGH_VALUE = 0.8
PRODUCTIVITY_KEY = {
    PRODUCTIVITY.HIGH: lambda hdi: hdi > HIGH_VALUE,
    PRODUCTIVITY.LOW: lambda hdi: hdi <= HIGH_VALUE
}


def _get_productivity(country: dict, default: PRODUCTIVITY = PRODUCTIVITY.HIGH):
    hdi = safe_parse_float(get_lookup_value(country, 'hdi'), None)
    return next((key for key in PRODUCTIVITY_KEY if hdi and PRODUCTIVITY_KEY[key](hdi)), default)
