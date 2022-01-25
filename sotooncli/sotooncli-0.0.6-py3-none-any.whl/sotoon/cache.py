import click

from sotooncli.cache_utils import CacheUtils
from sotooncli.core.decorators import group


@group()
def cache(**_):
    """manages cache"""
    pass


@cache.command()
def update(**_):
    """updates cache and exits"""
    CacheUtils().update_cache()
    click.echo("Cache updated successfully.")


@cache.command()
def remove(**_):
    """removes existing cache"""
    CacheUtils().remove_cache()
    click.echo("Cache removed successfully.")
