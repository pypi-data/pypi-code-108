import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

import click
import yaml

from sotooncli.config_utils import (
    get_active_config_name,
    read_user_config,
    set_config,
    write_to_user_config,
)
from sotooncli.core.decorators import argument, group
from sotooncli.settings import (
    ACTIVE_CONFIG,
    APP_CONFIG_NAME,
    APP_DIR,
    USER_CONFIG_DIR_NAME,
    USER_DEFAULT_CONFIG_NAME,
)
from sotooncli.utils import delete_file, get_strerror, read_yaml_file, write_to_yaml


@group()
def config(**_):
    """view and edit configs."""
    if not os.path.exists(f"{APP_DIR}/{USER_CONFIG_DIR_NAME}") or not os.path.isfile(
        f"{APP_DIR}/{APP_CONFIG_NAME}"
    ):
        dirs = [APP_DIR, f"{APP_DIR}/{USER_CONFIG_DIR_NAME}"]
        files = [APP_CONFIG_NAME, f"{USER_CONFIG_DIR_NAME}/{USER_DEFAULT_CONFIG_NAME}"]
        default_config = {ACTIVE_CONFIG: USER_DEFAULT_CONFIG_NAME}
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
        for file_path in files:
            file = Path(f"{APP_DIR}/{file_path}")
            file.touch(exist_ok=True)
        with open(f"{APP_DIR}/{APP_CONFIG_NAME}", mode="w") as config_file:
            yaml.dump(default_config, config_file)


@config.command()
@argument("key", placeholder="KEY", is_required=True)
def get(**kwargs):
    """get the key's value from the active config"""
    key = kwargs["key"]
    active_config = get_active_config_name()
    config_data = read_user_config(active_config)
    if key not in config_data:
        raise click.BadParameter("No such property is set in the active config")
    click.echo(config_data[key])


@config.command(name="list")
def list_configs(**_):
    """get active config's values"""
    active_config = get_active_config_name()
    config_data = read_user_config(active_config)
    click.echo(config_data)


@config.command()
@argument("key", placeholder="KEY", is_required=True)
@argument("value", placeholder="VALUE", is_required=True)
def set(**kwargs):
    """set the value to key in the active config."""
    key = kwargs["key"]
    value = kwargs["value"]
    set_config(key, value)
    click.echo(f"Set {key} to {value}")


@config.command()
@argument("key", placeholder="KEY", is_required=True)
def unset(**kwargs):
    """unset the value to key in the active config."""
    key = kwargs["key"]
    active_config = get_active_config_name()
    config_data = read_user_config(active_config)
    if key not in config_data:
        raise click.BadParameter(
            f'No such property "{key}" is set in the active config.'
        )
    config_data.pop(key)
    write_to_user_config(active_config, config_data)
    click.echo(f"Unset {key}")


@config.group()
def configurations(**_):
    """Manages the set of named configurations"""


@configurations.command()
@argument("name", placeholder="CONFIG_NAME", is_required=True)
def create(**kwargs):
    """Creates a new named configuration."""
    name = kwargs["name"]
    path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{name}.yaml"
    file = Path(path)
    if file.is_file():
        raise click.BadParameter(f'A configuration with name "{name}" already exists.')
    file.touch()
    click.echo(f"Created {name} config.")


@configurations.command()
@argument("name", placeholder="CONFIG_NAME", is_required=True)
def delete(**kwargs):
    """Deletes a named configuration."""
    name = kwargs["name"]
    path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{name}.yaml"
    try:
        delete_file(path)
    except FileNotFoundError:
        raise click.BadParameter("No such config.")
    except Exception as e:
        raise click.BadParameter(f"Could not delete Config: {get_strerror(e)}")
    click.echo(f"Deleted {name} config.")


@configurations.command()
@argument("name", placeholder="CONFIG_NAME", is_required=True)
def activate(**kwargs):
    """Activates an existing named configuration."""
    name = kwargs["name"]
    user_config_path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}/{name}.yaml"
    if not os.path.isfile(user_config_path):
        raise click.BadParameter("No such config.")
    app_config_path = f"{APP_DIR}/{APP_CONFIG_NAME}"
    config_data = read_yaml_file(app_config_path) or {}
    config_data[ACTIVE_CONFIG] = f"{name}.yaml"
    write_to_yaml(app_config_path, config_data)
    click.echo(f"Set active config to {name}")


@configurations.command()
@argument("name", placeholder="CONFIG_NAME", is_required=True)
def describe(**kwargs):
    """Describes a named configuration by listing its key-value."""
    name = kwargs["name"]
    config_data = read_user_config(f"{name}.yaml")
    click.echo(config_data)


@configurations.command(name="list")
def list_commands(**_):
    """Lists existing named configurations."""
    path = f"{APP_DIR}/{USER_CONFIG_DIR_NAME}"
    files = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f))]
    click.echo(files)
