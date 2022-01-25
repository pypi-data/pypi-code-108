import json
import os

import click
import yaml

ERROR_LOAD_FILE = "Could not load file: {path}: {error}"
ERROR_WRITE_TO_FILE = "Could not write to file: {path}: {error}"


def get_strerror(e, default=None):
    if hasattr(e, "strerror"):
        msg = e.strerror
    else:
        if default is not None:
            msg = default
        else:
            msg = str(e)
    return msg


def read_yaml_file(path):
    try:
        with open(path) as f:
            config_data = yaml.safe_load(f)
            return config_data
    except Exception as e:
        raise click.ClickException(
            ERROR_LOAD_FILE.format(path=path, error=get_strerror(e))
        )


def write_to_yaml(path, value):
    try:
        with open(path, mode="w") as file:
            yaml.dump(value, file)
    except Exception as e:
        raise click.ClickException(
            ERROR_WRITE_TO_FILE.format(path=path, error=get_strerror(e))
        )


def delete_file(path):
    if not os.path.isfile(path):
        raise FileNotFoundError
    try:
        os.remove(path)
    except Exception as e:
        raise click.BadParameter(f"Could not delete file: {get_strerror(e)}")


def read_json(path):
    if not os.path.isfile(path):
        raise FileNotFoundError
    try:
        with open(path) as json_file:
            data = json.load(json_file)
            return data
    except Exception as e:
        raise click.ClickException(
            ERROR_LOAD_FILE.format(path=path, error=get_strerror(e))
        )


def write_to_json(path, value):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w") as outfile:
            json.dump(value, outfile)
    except Exception as e:
        raise click.ClickException(
            ERROR_WRITE_TO_FILE.format(path=path, error=get_strerror(e))
        )
