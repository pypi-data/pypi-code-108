import os
from enum import Enum
import logging
import requests
from requests.exceptions import HTTPError
from typing import Dict


def generate_headers(api_key: str) -> Dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Rasgo-Client": "PyRasgo"
    }


class InvalidApiKeyException(Exception):
    pass


class Environment(Enum):
    PRODUCTION = "api.rasgoml.com"
    STAGING = "staging-rasgo-proxy.herokuapp.com"
    LOCAL = "localhost"

    @classmethod
    def from_environment(cls):
        return cls(os.getenv("RASGO_DOMAIN", cls.PRODUCTION))

    @property
    def app_path(self):
        if self == self.PRODUCTION:
            return 'https://app.rasgoml.com'
        if self == self.STAGING:
            return 'https://dev.rasgoml.com'
        if self == self.LOCAL:
            return 'http://localhost:9000'

class SessionMeta(type):
    _api_key = None
    _profile = None
    _environment = None

    def __new__(mcs, name, bases, dct):
        new = super().__new__(mcs, name, bases, dct)
        logging.debug(f'Starting the session for user')
        new._environment = Environment.from_environment()
        new._api_key = mcs._api_key or None
        new._profile = mcs._profile or None
        return new

    def __call__(cls, *args, **kwargs):
        if SessionMeta._api_key is None:
            api_key = kwargs.pop("api_key", None)
            if not api_key:
                raise ValueError("Must provide an API key to access the endpoint")
            SessionMeta._api_key = api_key
        if SessionMeta._environment is None:
            SessionMeta._environment = Environment.from_environment()
        if SessionMeta._profile is None:
            protocol = 'http' if SessionMeta._environment.value == 'localhost' else 'https'
            response = requests.get(
                f"{protocol}://{SessionMeta._environment.value}/v1/users/me",
                headers=generate_headers(SessionMeta._api_key)
            )
            try:
                response.raise_for_status()
            except HTTPError:
                raise InvalidApiKeyException(
                    f"The API key provided ({SessionMeta._api_key[:5]}...{SessionMeta._api_key[-5:]}) "
                    f"is not valid.")
            SessionMeta._profile = response.json()
        cls._api_key = SessionMeta._api_key
        cls._profile = SessionMeta._profile
        cls._environment = SessionMeta._environment
        return type.__call__(cls, *args, **kwargs)


class Session(metaclass=SessionMeta):
    pass

    @property
    def api_key(self):
        return self._api_key

    @property
    def profile(self):
        return self._profile
