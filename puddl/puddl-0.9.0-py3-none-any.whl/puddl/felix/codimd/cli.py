#!/usr/bin/env python
import logging
import os
import runpy
from pathlib import Path

import click
import sqlalchemy

from puddl.db import get_alchemy_session
from puddl.db.alchemy import get_engine

log = logging.getLogger()


class CodiMDError(Exception):
    pass


@click.group()
def main():
    pass


def get_remotes(ctx, args, incomplete):
    from puddl.felix.codimd.models import Remote
    session = get_alchemy_session()
    return session.query(Remote.name).all()


@main.command()
@click.argument('remote_name', autocompletion=get_remotes, envvar='CODIMD_NAME')
def index(remote_name):
    os.environ['CODIMD_NAME'] = remote_name
    # Run the "script"; it should not be imported, but be run from an interpreter.
    # We could create a subprocess, but choose to use this process' interpreter instead.
    runpy.run_module('puddl.felix.codimd.index')


@main.command()
def ls():
    import pandas as pd
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM codimd.cli_ls", engine, index_col='id')
    print(df)


@main.group()
def db():
    pass


@db.command()
def create():
    from puddl.felix.codimd.models import Base
    logging.getLogger('sqlalchemy').setLevel(log.level)
    engine = get_engine()
    engine.execute('CREATE SCHEMA IF NOT EXISTS codimd')
    Base.metadata.create_all(engine)
    views_path = Path(__file__).parent / 'views.sql'
    with views_path.open(encoding='utf-8') as f:
        engine.execute(sqlalchemy.text(f.read()))


@db.command()
@click.option('-f', '--force', is_flag=True)
def drop(force):
    q = 'DROP SCHEMA codimd CASCADE'
    if not force:
        click.confirm(f'Will run "{q}"; are you sure?', abort=True)
    logging.getLogger('sqlalchemy').setLevel(log.level)
    engine = get_engine()
    engine.execute(q)
