
from decouple import Config, config, RepositoryIni

from pathlib import Path

from typing import Any, cast, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = Path.home() / '.canvas' / 'config.ini'
DEFAULT_CONFIG_SECTION = 'canvas_cli'


INTEGRATION_SERVICE_ENDPOINT = config('INTEGRATION_SERVICE_ENDPOINT', '')

INTEGRATION_SERVICE_USERNAME = config('INTEGRATION_SERVICE_USERNAME', '')
INTEGRATION_SERVICE_PASSWORD = config('INTEGRATION_SERVICE_PASSWORD', '')

IS_HEALTHCHEC = True


def read_config(config_name: Optional[str] = None) -> Dict[str, Any]:

    if config_name is None:
        config_name = DEFAULT_CONFIG_SECTION

    try:
        ini = RepositoryIni(CONFIG_PATH)
    except FileNotFoundError:
        raise FileNotFoundError(
            f'Please add your configuration at "{CONFIG_PATH}"; you can set '
            'defaults using `canvas-cli create-default-settings`.')

    if not ini.parser.has_section(config_name):
        raise ValueError(
            f'Settings file "{settings.CONFIG_PATH}" does not contain section "{config_name}"; '
            'you can set defaults using `canvas-cli create-default-settings`.')

    ini.SECTION = config_name
    config = Config(ini)

    config: Dict[str, Any] = {
        'url': config('url', cast=str),
        'api_key': config('api-key', cast=str)
    }

    return config
