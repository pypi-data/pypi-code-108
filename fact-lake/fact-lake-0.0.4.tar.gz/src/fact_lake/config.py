import logging
from os import environ as env
from pathlib import Path
from typing import Any, Optional, Dict, Tuple, Type, TypeVar, List
from pyfactcast.client.config import ClientConfiguration, Credentials
from pydantic import BaseSettings, validator

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


C = TypeVar("C", bound="AppConfiguration.Config")


class AppConfiguration(BaseSettings):
    cryptoshred_init_vector: str = ""
    decrypt: bool = True
    mongo_username: str
    mongo_password: str
    factcast_server: str = "localhost"
    factcast_user: Optional[str] = None
    factcast_password: Optional[str] = None
    factcast_root_cert_path: Optional[str] = None
    factcast_cn_overwrite: Optional[str] = None
    factcast_insecure: bool = False
    mongo_server: str = "localhost"
    mongo_port: int = 27017
    mongo_tls: bool = False
    mongo_tls_invalid_certificates: bool = False
    mongo_tls_ca_file_path: Optional[str] = None
    mongodb_retry_writes: bool = False
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
    if config.factcast_user:
        credentials = Credentials(
            username=config.factcast_user, password=config.factcast_password
        )

    return ClientConfiguration(
        server=config.factcast_server,
        root_cert_path=config.factcast_root_cert_path,
        ssl_target_override=config.factcast_cn_overwrite,
        credentials=credentials,
        insecure=config.factcast_insecure,
    )
