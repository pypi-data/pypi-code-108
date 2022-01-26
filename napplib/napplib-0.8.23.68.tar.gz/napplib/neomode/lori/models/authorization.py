from dataclasses import dataclass


@dataclass
class Authorization:
    token: str
    expiration_time: int
    last_updated: str
    environment: str
    client_id: str
    client_secret: str
    username: str
    password: str
    scope: str

