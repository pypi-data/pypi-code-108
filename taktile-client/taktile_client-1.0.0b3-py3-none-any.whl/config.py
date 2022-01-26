"""
Environment config
"""
import importlib.util
import json
import typing as t
from locale import getpreferredencoding
from pathlib import Path

import pkg_resources
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Env Configuration
    """

    API_V1_STR: str = "/api/v1"

    DEBUG: bool = False
    WEB_URL: str = "https://app.taktile.com"
    TAKTILE_API_URL: str = "https://taktile-api.taktile.com"
    DEPLOYMENT_API_URL: str = "https://deployment-api.taktile.com"

    TAKTILE_API_KEY: t.Optional[str] = None
    TAKTILE_CONFIG_FILE: Path = Path("~/.config/tktl/config.json").expanduser()

    # Used to set the size of each arrow batch in MB. This setting
    # gets overridden if batch size is set via `nrows` property.
    ARROW_BATCH_MB: float = 5

    # Should this client support communication to prereleases?
    ALLOW_PRERELEASE: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Env config"""

        case_sensitive = True


settings = Settings()

arrow_available = (
    importlib.util.find_spec("pandas") is not None
    and importlib.util.find_spec("numpy") is not None
    and importlib.util.find_spec("pyarrow") is not None
    and importlib.util.find_spec("certifi") is not None
)

version = pkg_resources.get_distribution(
    __name__.split(".", maxsplit=1)[0]
).version


def collect_api_key() -> t.Optional[str]:
    """collect_api_key
    If an api key is available in the TAKTILE_API_KEY environment variable,
    that one will be used. Otherwise, the taktile config file is read and
    the api key is obtained from there.

    Returns
    -------
    t.Optional[str]
        the API key, if found, else None
    """
    if settings.TAKTILE_API_KEY:
        return settings.TAKTILE_API_KEY

    if settings.TAKTILE_CONFIG_FILE.exists():
        encoding = getpreferredencoding(False)
        with settings.TAKTILE_CONFIG_FILE.open("r", encoding=encoding) as cfg:
            config = json.load(cfg)
        if "api-key" in config:
            return str(config["api-key"])
    return None
