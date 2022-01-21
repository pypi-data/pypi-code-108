from os import name
import click

from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_config,
    cmd_error,
    cmd_info,
    cmd_success,
    get_cmd_command,
)

@click.group("config")
def commands():
    """
    Get or set project's options.
    """
    pass


@commands.command()
@check_config()
@get_cmd_command()
def ls():
    """
    Print full config in current project.
    """
    config = AnylearnCliConfig.load()
    cmd_info(msg=str(config))


@commands.command()
@click.argument('config_key')
@check_config()
@get_cmd_command()
def get(config_key: str):
    """
    Get config by key.
    """
    config = AnylearnCliConfig.load()
    try:
        val = config.gets(config_key=config_key)
        cmd_info(msg=val)
    except Exception as e:
        cmd_error(msg=str(e))
        raise click.Abort


@commands.command()
@click.argument('config_key')
@click.argument('value')
@check_config()
@get_cmd_command()
def set(config_key: str, value):
    """
    Set config by key.
    """
    config = AnylearnCliConfig.load()
    try:
        config.sets(config_key=config_key, value=value)
        AnylearnCliConfig.update(config)
        cmd_success(msg="OK")
    except Exception as e:
        cmd_error(msg=str(e))
        raise click.Abort
