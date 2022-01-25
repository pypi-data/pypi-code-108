"""Validation functions specific to the test plan commands"""

import os
from typing import Optional

import click
import yaml

from ..docker_utils import is_docker, map_hostpath_to_container
from ..utils import file_exists


def validate_envfile_exists(
    ctx: click.core.Context, param: click.core.Parameter, raw_value: str
) -> Optional[str]:
    if not raw_value:
        click.secho(
            "No env file specified. Attempting to run test plan without an env file.\n"
            'Please try specifying a path to a valid env file with "--env-file <path>" if you face any issues.',
            fg="yellow",
        )
        return None

    """Check if the env file exists and it's a valid YAML file. On error display error message and end execution"""
    if is_docker() and os.path.isabs(raw_value):
        click.secho(
            "The env file must be relative to the current working directory", fg="red"
        )
        raise click.exceptions.Exit(1)

    mapped_file: str = map_hostpath_to_container(raw_value)

    if not file_exists(mapped_file):
        click.secho(
            "Cannot access the specified environmental YAML file.\n"
            "Please ensure the specified env file path is relative to the CLI's working directory.",
            fg="red",
        )
        raise click.exceptions.Exit(1)

    # Check if the file is a valid YAML file
    try:
        yaml.full_load(open(mapped_file))
    except yaml.YAMLError as e:
        click.secho(
            "Please ensure the specified YAML file is a valid YAML file.",
            fg="red",
        )
        raise click.exceptions.Exit(1)

    return mapped_file
