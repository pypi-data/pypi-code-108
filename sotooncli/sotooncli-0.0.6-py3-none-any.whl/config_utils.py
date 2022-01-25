from os.path import isfile

import click

from sotooncli.settings import (
    ACTIVE_CONFIG,
    APP_CONFIG_NAME,
    APP_DIR,
    USER_CONFIG_DIR_NAME,
)
from sotooncli.utils import read_yaml_file, write_to_yaml


def get_active_config_name():
    app_config_path = f"{APP_DIR}/{APP_CONFIG_NAME}"
    if not isfile(app_config_path):
        raise click.UsageError(message=f"App config is not found in {app_config_path}")
    config_data = read_yaml_file(app_config_path)
    if ACTIVE_CONFIG not in config_data:
        raise click.UsageError(message="No active config found")
    return config_data[ACTIVE_CONFIG]


def get_active_config_path():
    return f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{get_active_config_name()}"


def read_user_config(name):
    config_path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{name}"
    config_data = read_yaml_file(config_path)
    return config_data


def write_to_user_config(name, value):
    config_path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{name}"
    write_to_yaml(config_path, value)


def set_config(key, value):
    active_config = get_active_config_name()
    config_data = read_user_config(active_config) or {}
    config_data[key] = value
    write_to_user_config(active_config, config_data)
