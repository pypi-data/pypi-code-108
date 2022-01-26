from __future__ import annotations
from typing import Any, List
from enum import Enum

import configparser
import os
from pathlib import Path

from .config import Config
from .lunar_client import LunarError
from .data import BatchClient, DataClient, DatasetClient, QueryClient
from .ml import EDDService, ModelRegistry, LunarModel
from .rec import ChannelClient, ExperimentClient, RecommendationClient


LUNAR_CREDENTIALS_PATH = ".lunar/credentials"

SERVICE_CLIENT_MAP = {
    "channel": {"client": ChannelClient, "api_type": "REC", "path": "/v1/channels"},
    "experiment": {"client": ExperimentClient, "api_type": "REC", "path": "/v1/experiments"},
    "recommend": {"client": RecommendationClient, "api_type": "REC", "path": "/v1/recommend"},
    "batch": {"client": BatchClient, "api_type": "DATA", "path": "/v1/batch"},
    "data": {"client": DataClient, "api_type": "DATA", "path": "/v1/data"},
    "dataset": {"client": DatasetClient, "api_type": "DATA", "path": "/v1/datasets"},
    "query": {"client": QueryClient, "api_type": "DATA", "path": "/v1/query"},
}


class LunarEnv(Enum):
    """
    Lunar environments.
    """

    LOCAL = "LOCAL"
    DEV = "DEV"
    STG = "STG"
    PRD = "PRD"

    @classmethod
    def list_items(cls) -> List[LunarEnv]:
        """
        Return all names of Lunar environments
        """
        return [t for t in cls]

    @classmethod
    def list_values(cls) -> List[str]:
        """
        Return all values of Lunar environments
        """
        return [t.value for t in cls]


class RuntimeEnv(Enum):
    """
    Runtime environments.
    """

    LOCAL = "LOCAL"
    EDD = "EDD"
    BAP = "BAP"

    @classmethod
    def list_items(cls) -> List[RuntimeEnv]:
        """
        Return all names of Runtime environments
        """
        return [t for t in cls]

    @classmethod
    def list_values(cls) -> List[str]:
        """
        Return all values of Runtime environments
        """
        return [t.value for t in cls]


def _init_config(env: str = None, apikey: str = None, runtime_env: str = None) -> Config:
    env = env or os.getenv("LUNAR_ENV")
    apikey = apikey or os.getenv("LUNAR_APIKEY")
    runtime_env = runtime_env or os.getenv("LUNAR_RUNTIME")
    runtime_env = runtime_env.upper() if runtime_env else runtime_env

    if not env or not apikey:
        credential_path = Path.home().joinpath(LUNAR_CREDENTIALS_PATH)
        if not os.path.exists(credential_path):
            raise LunarError(code=404, msg="Credential file does not exist")

        config = configparser.ConfigParser()
        config.read(credential_path)

        if env:
            for section in config.values():
                if section.get("env") == env:
                    apikey = section.get("apikey")
                    break

            if not apikey:
                raise LunarError(code=404, msg=f"No profile defined for env `{env}` in the credential file")

        else:
            lunar_profile = os.environ.get("LUNAR_PROFILE") or "default"
            if not config.has_section(lunar_profile):
                raise LunarError(code=404, msg=f"Credential file does not have `{lunar_profile}` section")

            section = config[lunar_profile]
            try:
                apikey = section["apikey"]
                env = section["env"]
            except KeyError as e:
                raise LunarError(code=404, msg=f"Credential file does not have a key `{str(e)}`")

    try:
        config = Config(env=env.upper(), apikey=apikey, runtime_env=runtime_env)
    except AttributeError:
        raise LunarError(code=404, msg=f"`Config` does not exist for env {env}")

    return config


def client(service_name: str = None, env: str = None, apikey: str = None, runtime_env: str = None) -> Any:
    """
    Create a client object for lunar API.

    ## Args

    - service_name: (optional) (str) The name of a service for the client
    - env: (optional) (str) The name of a environment for lunar API (`local`|`dev`|`stg`|`prd`)
    - apikey: (optional) (str) The access apikey for lunar API
    - runtime_env: (optional) (str) The name of a runtime environment (`local`|`edd`|`bap`)

    ## Example

    ```python
    import lunar

    client = lunar.client("channel")
    ```
    """
    if env:
        assert env.upper() in LunarEnv.list_values(), "`env` must be one of `local`|`dev`|`stg`|`prd`"
    if runtime_env:
        assert runtime_env.upper() in RuntimeEnv.list_values(), "`runtime_env` must be one of `local`|`edd`|`bap`"

    try:
        client_map = SERVICE_CLIENT_MAP[service_name]
    except KeyError:
        raise LunarError(code=404, msg=f"`service_name` {service_name} is not supported.")

    config = _init_config(env=env, apikey=apikey, runtime_env=runtime_env)
    config.__setattr__("URL", config.__dict__[f"LUNAR_{client_map['api_type'].upper()}_URL"])
    config.__setattr__("API_PATH", client_map["path"])

    return client_map["client"](config)


def model_registry(env: str = None, apikey: str = None, runtime_env: str = None) -> ModelRegistry:
    config = _init_config(env=env, apikey=apikey, runtime_env=runtime_env)
    config.__setattr__("URL", config.__dict__["LUNAR_DATA_URL"])
    return ModelRegistry(config)


def edd(env: str = None, apikey: str = None, runtime_env: str = None) -> EDDService:
    config = _init_config(env=env, apikey=apikey, runtime_env=runtime_env)
    config.__setattr__("URL", config.__dict__["LUNAR_DATA_URL"])
    config.__setattr__("API_PATH", SERVICE_CLIENT_MAP["batch"]["path"])
    return EDDService(config)


model = LunarModel
