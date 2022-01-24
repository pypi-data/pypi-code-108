"""Console script for baseten."""
import configparser
import functools
import json
import logging
import sys
from urllib.parse import urlparse

import click

from baseten.common import api
from baseten.common.settings import read_config, set_config_value
from baseten.common.util import setup_logger

logger = logging.getLogger(__name__)


def ensure_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = read_config()
        try:
            config.get('api', 'api_key')
        except configparser.NoOptionError:
            click.echo('You must first run the `baseten login` cli command.')
            sys.exit()
        result = func(*args, **kwargs)
        return result
    return wrapper


@click.group()
def cli_group():
    setup_logger('baseten', logging.INFO)


@cli_group.command()
@click.option('--server_url', prompt='BaseTen server URL')
def configure(server_url):
    if not _is_valid_url(server_url):
        click.echo('That is not a valid URL.')
        return
    set_config_value('api', 'url_base', server_url)
    click.echo('Saved server URL.')


@cli_group.command()
@click.option('--api_key', prompt='BaseTen API key', hide_input=True)
def login(api_key):
    set_config_value('api', 'api_key', api_key)
    click.echo('Saved API key.')


@cli_group.command()
@ensure_login
def models():
    user_models = api.models()
    click.echo('Your models:\n{}'.format(json.dumps(user_models, indent=4)))


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


if __name__ == '__main__':
    cli_group()
