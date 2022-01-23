"""
config for :mod:`photoResizer` application.

:creationdate:  13/12/2021 20:09
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: photoResizer.config
"""
import logging
from functools import lru_cache
from logging import config
from pathlib import Path
from typing import Dict

import yaml

__author__ = "fguerin"
logger = logging.getLogger(__name__)


def load_config(config_file: Path) -> Dict:
    """
    Loads the configuration file.
    """
    with config_file.open() as f:
        return yaml.load(f, Loader=yaml.FullLoader)


@lru_cache(maxsize=1)
def get_config(config_file: Path) -> Dict:
    """
    Returns the configuration dictionary.
    """
    return load_config(config_file)


def load_logger_config(config_file: Path) -> None:
    """
    Returns the logger configuration dictionary.
    """
    config.dictConfig(get_config(config_file)["logging"])
