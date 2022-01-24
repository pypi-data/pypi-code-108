import click
from clease.db_util import (get_all_cf_names, get_all_cf, get_cf_tables)
from . import main


@main.clease_cli.group()
def db():
    """The DB CLI"""


@db.command(help='Display the available correlation function tables')
@click.argument('db_name', type=str)
def tab(db_name):
    show_cf_tables(db_name)


@db.command(help='Display the available CF names in the DB')
@click.argument('db_name', type=str)
def names(db_name):
    show_cf_names(db_name)


@db.command(help='Display the correlation functions for a specific ID in the database')
@click.argument('db_name', type=str)
@click.argument('db_id', type=int)
def cf(db_name, db_id):
    try:
        show_cf(db_name, db_id)
    except Exception as exc:  # pylint: disable=broad-except
        click.echo(f'An error occurred: {exc}')


def show_cf_tables(db_name: str):
    tables = get_cf_tables(db_name)
    cftab = ', '.join(tables)
    click.echo(f"Available correlation function tables: {cftab}")


def show_cf_names(db_name: str):
    table = get_cf_tables(db_name)[0]
    cf_names = sorted(get_all_cf_names(db_name, table))
    click.echo("Tracked correlation functions")

    line = ""
    char_per_line = 110
    for name in cf_names:
        if len(line) + len(name) > char_per_line:
            click.echo(line)
            line = ""
        if line == "":
            line += name
        else:
            line += ', ' + name
    click.echo(line)


def show_cf(db_name: str, db_id: int):
    table = get_cf_tables(db_name)[0]
    cfs = get_all_cf(db_name, table, db_id)
    click.echo(f"Correlation functions for ID {db_id}")
    for k, v in cfs.items():
        click.echo(f"{k}: {v}")
