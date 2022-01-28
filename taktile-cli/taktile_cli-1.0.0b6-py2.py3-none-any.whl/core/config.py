import errno
import json
import os
from locale import getpreferredencoding
from pathlib import Path
from typing import Dict, Optional

from filelock import SoftFileLock
from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    LOCAL_STACK: bool = False
    E2E: bool = False
    CI_RUNNER_NAME: Optional[str] = None

    VERBOSE: bool = False
    DEBUG: bool = False
    WEB_URL: str = "https://app.taktile.com"
    TAKTILE_API_URL: str = "https://taktile-api.taktile.com"
    DEPLOYMENT_API_URL: str = "https://deployment-api.taktile.com"

    TAKTILE_CONFIG_FILE: Path = Path(
        "~/.config/tktl/config.json"
    ).expanduser().absolute()
    HELP_HEADERS_COLOR: str = "yellow"
    HELP_OPTIONS_COLOR: str = "green"
    USE_CONSOLE_COLORS: bool = True
    HELP_COLORS_DICT: Dict = {
        "help_headers_color": "yellow",
        "help_options_color": "green",
    }

    LOCAL_ARROW_ENDPOINT: str = "grpc://127.0.0.1:5005"
    LOCAL_REST_ENDPOINT: str = "http://127.0.0.1:8080"
    ARROW_BATCH_MB: int = 50
    PARQUET_BATCH_DEFAULT_ROWS_READ: int = int(1e6)

    FUTURE_ENDPOINTS: bool = True
    TAKTILE_PROFILING_VERSION: Optional[str] = os.environ.get(
        "TAKTILE_PROFILING_VERSION"
    )

    class Config:
        case_sensitive = True


settings = Settings()


def set_api_key(api_key: Optional[str]):
    """set_api_key
    Stores a specified API key in the config file at `TAKTILE_CONFIG_FILE`

    Parameters
    ----------
    api_key : str
        API key to set in the config file
    """

    encoding = getpreferredencoding(False)
    config_path = settings.TAKTILE_CONFIG_FILE
    try:
        os.makedirs(config_path.parent)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

    with SoftFileLock(f"{config_path}.lock", timeout=1):
        if config_path.exists():
            with config_path.open("r", encoding=encoding) as config_file:
                config = json.load(config_file)
        else:
            config = {}

        if api_key is None:
            if "api-key" in config:
                del config["api-key"]
        else:
            config["api-key"] = api_key

        with config_path.open("w", encoding=encoding) as config_file:
            json.dump(config, config_file, indent=2, sort_keys=True)
            config_file.write("\n")
