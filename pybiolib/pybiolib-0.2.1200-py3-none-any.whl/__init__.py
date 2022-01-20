import os

from biolib import typing_utils
from biolib.app import BioLibApp as _BioLibApp
from biolib.biolib_logging import logger as _logger
from biolib.biolib_api_client import BiolibApiClient as _BioLibApiClient

import biolib.app
import biolib.cli
import biolib.utils


# ------------------------------------ Function definitions for public Python API ------------------------------------

def call_cli() -> None:
    biolib.cli.main()


def load(uri: str) -> _BioLibApp:
    return _BioLibApp(uri)


def set_api_base_url(api_base_url: str) -> None:
    _BioLibApiClient.initialize(base_url=api_base_url)


def set_api_token(api_token: str) -> None:
    _BioLibApiClient.get().login(api_token)


def set_log_level(level: typing_utils.Union[str, int]) -> None:
    _logger.setLevel(level)


# -------------------------------------------------- Configuration ---------------------------------------------------
__version__ = biolib.utils.BIOLIB_PACKAGE_VERSION
_logger.configure(default_log_level='INFO')

set_api_base_url(os.getenv('BIOLIB_BASE_URL', default='https://biolib.com'))
