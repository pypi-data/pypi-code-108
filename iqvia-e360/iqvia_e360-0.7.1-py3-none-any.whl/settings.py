from typing import Optional
import logging
import pathlib
import dataclasses
import configparser


@dataclasses.dataclass
class Settings:
    """
    Dataclass for holing environment variables with defaults
    """
    verify_ssl: bool = True
    log_level: int = logging.INFO
    settings_path: pathlib.Path = pathlib.Path("e360.ini")

    # Api Gatway Credentials
    api_gateway_url: str = "https://fhmsweb05.internal.imsglobal.com:20666/"
    api_gateway_key: Optional[str] = None

    # OIDC credentials
    use_oidc_mode: bool = False
    oidc_user_id: Optional[str] = None
    oidc_endpoint_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    service_directory_url: Optional[str] = None

    _default_config_namespace = 'e360'

    def __post_init__(self) -> None:
        """
        Collects any environment variables, and reassigns them in the class
        """
        if self.settings_path.is_file():
            config = configparser.ConfigParser()
            config.read(self.settings_path)
            e360_config = config[self._default_config_namespace]
            for key, dtype in self.__annotations__.items():
                if key in e360_config:
                    if dtype == bool:
                        value = e360_config.getboolean(key)
                    else:
                        value = e360_config[key]  # type: ignore
                    setattr(self, key, value)
        if not (self.is_api_gateway_mode or self.is_oidc_mode):
            raise ValueError(f"Settings not valid for either Api Gateway or OIDC mode. Please review and try again. {self}")

    @property
    def is_api_gateway_mode(self) -> bool:
        return bool(self.api_gateway_url and self.api_gateway_key and not self.use_oidc_mode)

    @property
    def is_oidc_mode(self) -> bool:
        return bool(self.oidc_endpoint_url and self.oidc_client_id and self.oidc_client_secret and self.service_directory_url and self.use_oidc_mode)
