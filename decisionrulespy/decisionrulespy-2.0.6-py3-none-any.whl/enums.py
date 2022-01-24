import enum


class GeoLocations(enum.Enum):
    DEFAULT = "default"
    EU1 = "eu1"
    EU2 = "eu2"
    US1 = "us1"
    US2 = "us2"


class SolverStrategies(enum.Enum):
    STANDARD = "STANDARD"
    ARRAY = "ARRAY"
    FIRST_MATCH = "FIRST_MATCH"


class Protocols(enum.Enum):
    HTTP = "http"
    HTTPS = "https"


class SolverType(enum.Enum):
    RULE = "rule"
    RULE_FLOW = "composition"
