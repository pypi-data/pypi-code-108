import click

from redbeard_cli.commands.lookups import (
    lookups as lookup_command
)


@click.group()
def lookup():
    pass


@lookup.command()
def datasets():
    lookup_command.ls_datasets()


@lookup.command()
def identities():
    lookup_command.ls_identity_types()

