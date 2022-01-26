from dataclasses import dataclass


@dataclass
class Authorization:
    token: str
    refresh_token: str
    expiration_time: int
    last_updated: str
    client_id: str
    client_secret: str
    url: str