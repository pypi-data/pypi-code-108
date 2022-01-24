import abc
import os
import time

import requests

CONFIG_FILE_NAME = "archimedes.toml"

USER_HOME_DIR = os.path.expanduser("~")
ARCHIMEDES_CONF_DIR = os.path.join(USER_HOME_DIR, ".archimedes")
SAVED_CONFIG_PATH = os.path.join(ARCHIMEDES_CONF_DIR, "arcl.json")
SAVED_MSAL_TOKEN_CACHE_PATH = os.path.join(ARCHIMEDES_CONF_DIR, "msal.cache.bin")

environment = os.environ.get("ENVIRONMENT", "prod").lower()

if not os.path.exists(ARCHIMEDES_CONF_DIR):
    os.mkdir(ARCHIMEDES_CONF_DIR)


ARCHIMEDES_API_CONFIG_URL = f"https://arcl.optimeering.no/config.json?timestamp={time.time()}"


class InvalidEnvironmentException(Exception):
    pass


class ApiConfig(abc.ABC):
    def __init__(self, env):
        config_result = requests.get(ARCHIMEDES_API_CONFIG_URL, headers={"Cache-Control": "no-cache"})
        self.config = config_result.json()
        if env not in self.config.keys():
            raise InvalidEnvironmentException(
                f"Invalid environment {env}, "
                f"supported values are {', '.join([str(key) for key in self.config.keys()])}"
            )
        self.environment = env.lower()

    def __getattr__(self, item):
        env_config = self.config[self.environment]
        return env_config[item]


api_config = ApiConfig(environment)
