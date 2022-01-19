from dataclasses import dataclass


DATAFOLD_APIKEY = "DATAFOLD_APIKEY"
DATAFOLD_HOST = "DATAFOLD_HOST"


@dataclass
class CliContext:
    host: str
    api_key: str
