from enum import Enum
from typing import Union


class DataType(Enum):
    SMALLINT = 'smallint'
    BIGINT = 'bigint'
    INT = 'int'
    INTEGER = 'integer'
    TINYINT = 'tinyint'
    BYTEINT = 'byteint'
    FLOAT = 'float'
    FLOAT4 = 'float4'
    FLOAT8 = 'float8'
    FLOAT64 = 'float64'
    DECIMAL = 'decimal'
    NUMERIC = 'numeric'
    NUMBER = 'number'
    REAL = 'real'
    DOUBLE = 'double'
    STRING = 'string'
    TEXT = 'text'
    VARCHAR = 'varchar'
    CHAR = 'char'
    CHARACTER = 'character'
    DATE = 'date'
    DATETIME = 'datetime'
    TIME = 'time'
    TIMESTAMP = 'timestamp'
    TIMESTAMP_LTZ = 'timestamp_ltz'
    TIMESTAMP_NTZ = 'timestamp_ntz'
    TIMESTAMP_TZ = 'timestamp_tz'
    BINARY = 'binary'
    VARBINARY = 'varbinary'
    BOOLEAN = 'boolean'
    BOOL = 'bool'
    VARIANT = 'variant'
    OBJECT = 'object'
    ARRAY = 'array'

class Granularity(Enum):
    """
    Enum class to describe allowed types of granularities
    """
    # TODO: This exists to support validation prior to posting from the API.
    #       For ease of maintenance, this should be handled through API returns.
    ACTION = 'action'
    ACTOR = 'actor'
    AIRLINE = 'airline'
    AIRPORT = 'airport'
    ATBAT = 'atbat'
    AUTHOR = 'author'
    BUYER = 'buyer'
    CBG = 'CBG'
    CITY = 'city'
    CLAIM = 'claim'
    COMPANY = 'company'
    COUNTY = 'county'
    COUNTRY = 'country'
    CUSTOM = 'custom'
    CUSTOMER = 'customer'
    DAY = 'day'
    DMA = 'DMA'
    FIPS = 'FIPS'
    FLIGHT = 'flight'
    GAME = 'game'
    HOUR = 'hour'
    LATLONG = 'latlong'
    MAKE = 'make'
    MEMBER = 'member'
    MINUTE = 'minute'
    MODEL = 'model'
    MONTH = 'month'
    MOVIE = 'movie'
    NAME = 'name'
    PAYER = 'payer'
    PLAY = 'play'
    PLAYER = 'player'
    PITCH = 'pitch'
    PRODUCT = 'product'
    PROVIDER = 'provider'
    PUBLISHER = 'publisher'
    QUARTER = 'quarter'
    SEASON = 'season'
    SECOND = 'second'
    STATE = 'state'
    STORE = 'store'
    STUDIO = 'studio'
    SUBSCRIBER = 'subscriber'
    TEAM = 'team'
    TERM = 'term'
    TICKER = 'ticker'
    TITLE = 'title'
    USER = 'user'
    UNIT = 'unit'
    WEEK = 'week'
    YEAR = 'year'
    ZIPCODE = 'zipcode'


class ModelTypes(Enum):
    """
    Enum class to describe allowed types of models
    """
    # TODO: This exists to support validation prior to posting from the API.
    #       For ease of maintenance, this should be handled through API returns.
    TIMESERIES = 'Timeseries'

    @classmethod
    def _missing_(cls, value):
        """ Sets up case-insensitive lookup """
        formatted = value.replace(" ", "").lower().capitalize()
        try:
            return cls._value2member_map_[formatted]
        except KeyError:
            raise ValueError("%r is not a valid %s" % (value, cls.__name__))


class ModelType(object):
    """
    Class to wrap the ModelTypes enum for additional functionality

    (Extending the enum class is not allowed, and subclassing is possible, but unnecessary)
    """

    def __init__(self, name: str):
        self._type = ModelTypes(name)
        # TODO: Lookup compatible when other model types and/or granularities are supported.
        self._compatible_granularities = [Granularity.DAY, Granularity.MONTH,
                                          Granularity.YEAR, Granularity.WEEK, Granularity.QUARTER]

    @property
    def name(self):
        return self._type.name

    @property
    def value(self):
        return self._type.value

    @property
    def compatible_granularities(self):
        return self._compatible_granularities

    def is_compatible(self, granularity: Union[str, Granularity]) -> bool:
        # If not enum, convert to enum first.
        try:
            granularity.name
        except AttributeError:
            granularity = Granularity(granularity)
        return granularity in self._compatible_granularities
