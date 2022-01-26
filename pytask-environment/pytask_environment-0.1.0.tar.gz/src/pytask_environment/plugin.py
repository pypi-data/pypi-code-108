"""Entry-point for the plugin."""
from _pytask.config import hookimpl
from pytask_environment import config
from pytask_environment import database
from pytask_environment import logging


@hookimpl
def pytask_add_hooks(pm):
    """Register some plugins."""
    pm.register(logging)
    pm.register(config)
    pm.register(database)
