import logging
from os import environ as env
from pathlib import Path
from typing import Any, Optional, Dict, Tuple, Type, TypeVar, List
from pyfactcast.client.config import ClientConfiguration, Credentials
from pydantic import BaseSettings, BaseModel, validator

log = logging.getLogger("fact-lake")

log_level_from_env = env.get("FACT_LAKE_LOG_LEVEL")
if log_level_from_env:
    log_level = getattr(
        logging,
        log_level_from_env.upper(),
    )  # Setting a default here is pretty defensive. Anyhow nothing lost by doing it
    log.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    return log.getChild(name)


class FactCastConfiguration(BaseModel):
    server: str = "localhost"
    user: Optional[str] = None
    password: Optional[str] = None
    root_cert_path: Optional[str] = None
    cn_overwrite: Optional[str] = None
    insecure: bool = False


class MongoDbCongifuration(BaseModel):
    username: str
    password: str
    server: str = "localhost"
    port: int = 27017


C = TypeVar("C", bound="AppConfiguration.Config")


class AppConfiguration(BaseSettings):
    factcast: FactCastConfiguration
    cryptoshred_init_vector: str = ""
    decrypt: bool = True
    mongo: MongoDbCongifuration
    whitelist: List[str] = []
    blacklist: List[str] = []

    @validator("blacklist")
    def only_black_or_white_list(
        cls, v: Any, values: Dict[str, Any], **kwargs: Dict[str, Any]
    ) -> None:
        if "whitelist" in values and values["whitelist"] and v:
            raise ValueError(
                "Whitelist and blacklist defined at the same time. Only define one."
            )

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls: Type[C],
            init_settings: Dict,
            env_settings: Dict,
            file_secret_settings: Dict,
        ) -> Tuple:
            return (env_settings, init_settings, file_secret_settings)


def get_configuration(
    profile: str = "default", *, config_dir: Path = Path.home().joinpath(".fact_lake")
) -> AppConfiguration:
    log.info("Getting Configuration")

    if profile:
        env_file_location = config_dir.joinpath(f"{profile}.env").absolute()
        return AppConfiguration(_env_file=env_file_location)

    return AppConfiguration()


def get_factcast_configuration(config: AppConfiguration) -> ClientConfiguration:
    credentials = None
    if config.factcast.user:
        credentials = Credentials(
            username=config.factcast.user, password=config.factcast.password
        )

    return ClientConfiguration(
        server=config.factcast.server,
        root_cert_path=config.factcast.root_cert_path,
        ssl_target_override=config.factcast.cn_overwrite,
        credentials=credentials,
        insecure=config.factcast.insecure,
    )
