from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ClientConfig:
    """Global options for a local client"""

    # default URL of Racetrack API server (Lifecycle URL)
    lifecycle_url: str = 'http://localhost:7002'

    # Git auth credentials set for particular repositories
    git_credentials: Dict[str, 'Credentials'] = field(default_factory=dict)

    # Racetrack URL aliases: alias name -> full URL to Lifecycle API
    lifecycle_url_aliases: Dict[str, str] = field(default_factory=dict)

    # User auth is base64 encoded json with username/token, per Lifecycle URL
    user_auths: Dict[str, str] = field(default_factory=dict)


@dataclass
class Credentials:
    username: str
    password: str
