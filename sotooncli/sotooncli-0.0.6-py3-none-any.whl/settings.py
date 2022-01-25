import os
from distutils.util import strtobool

import click

APP_NAME = "sotooncli"
SERVER_HOST = os.environ.get("SOTOON_SERVER_HOST", "https://gate.sotoon.ir/commander")
USE_CACHE = bool(strtobool(os.environ.get("SOTOON_USE_CACHE", "True")))
APP_DIR = click.get_app_dir(app_name=APP_NAME)
APP_CONFIG_NAME = "app_config.yaml"
USER_CONFIG_DIR_NAME = "configurations"
USER_DEFAULT_CONFIG_NAME = "config_default.yaml"
ACTIVE_CONFIG = "active_config"
