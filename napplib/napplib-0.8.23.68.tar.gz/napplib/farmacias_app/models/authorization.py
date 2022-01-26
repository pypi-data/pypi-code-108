from dataclasses import dataclass


@dataclass
class Authorization:
    token: str
    expiration_time: int
    last_updated: str
    client_id: str
    client_secret: str
    scope: str
    grant_type: str
    server_url: str