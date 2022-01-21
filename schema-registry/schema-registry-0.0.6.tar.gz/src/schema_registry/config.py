import logging
from pathlib import Path

from typing import Tuple, TypeVar, Type, Dict
from os import environ as env

from pydantic import BaseSettings

log = logging.getLogger("schema_registry")

log_level_from_env = env.get("SCHEMA_REGISTRY_LOG_LEVEL")
if log_level_from_env:

    log_level = getattr(
        logging,
        log_level_from_env.upper(),
    )
    logging.basicConfig(level=log_level)
    log.setLevel(log_level)

C = TypeVar("C", bound="Configuration.Config")


class Configuration(BaseSettings):
    schema_registry_url: str

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customize_sources(
            cls: Type[C],
            init_settings: Dict,
            env_settings: Dict,
            file_secret_settings: Dict,
        ) -> Tuple[Dict, Dict, Dict]:
            return (env_settings, init_settings, file_secret_settings)


def get_configuration(
    profile: str = "default",
    *,
    config_dir: Path = Path.home().joinpath(".schema_registry"),
) -> Configuration:
    log.info("Getting Configuration")

    if profile:
        env_file_location = config_dir.joinpath(f"{profile}.env").absolute()
        return Configuration(_env_file=env_file_location)

    return Configuration()


def get_logger(name: str) -> logging.Logger:
    return log.getChild(name)
