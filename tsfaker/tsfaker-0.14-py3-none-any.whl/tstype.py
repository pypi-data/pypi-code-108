# https://frictionlessdata.io/specs/table-schema/#types-and-formats
# Types
STRING = 'string'
NUMBER = 'number'
INTEGER = 'integer'
BOOLEAN = 'boolean'
OBJECT = 'object'
ARRAY = 'array'
DATE = 'date'
TIME = 'time'
DATETIME = 'datetime'
YEAR = 'year'
YEARMONTH = 'yearmonth'
DURATION = 'duration'
GEOPOINT = 'geopoint'
GEOJSON = 'geojson'
ANY = 'any'

implemented = [
    STRING,
    NUMBER,
    INTEGER,
    BOOLEAN,
    # OBJECT,
    # ARRAY,
    DATE,
    # TIME,
    DATETIME,
    YEAR,
    YEARMONTH,
    # DURATION,
    # GEOPOINT,
    # GEOJSON,
    # ANY,
]

# Date pattern
ISO8601_DATETIME_PATTERN = '%Y-%m-%dT%H:%M:%SZ'
ISO8601_DATE_PATTERN = '%Y-%m-%d'
YEAR_MONTH_PATTERN = '%Y%m'
YEAR_PATTERN = '%Y'
