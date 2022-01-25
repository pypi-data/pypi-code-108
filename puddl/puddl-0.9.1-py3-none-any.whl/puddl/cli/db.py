import logging
import os
import subprocess

import click
import psycopg2
import sqlalchemy

from puddl.cli.base import root
from puddl.conf import DBConfig
from puddl.db.tool import connect_to_db
from puddl.pg import DB, list_databases

log = logging.getLogger(__package__)


@root.command()
def init():
    """
    Initializes the database with stuff that puddl depends on, e.g. "FUNCTION puddl_upsert_role".
    """
    import pkg_resources

    conf = DBConfig()
    log.debug(conf.url)
    engine = sqlalchemy.create_engine(conf.url)

    pkg = 'puddl.pg'
    subdir = 'init_sql'
    files = pkg_resources.resource_listdir(pkg, subdir)
    resource_names = ['/'.join((subdir, f)) for f in files]
    for name in resource_names:
        log.debug(f'running file from pkg {pkg}: {name}')
        binary = pkg_resources.resource_string(pkg, name)
        txt = sqlalchemy.text(binary.decode('utf-8'))
        engine.execute(txt)


@root.command()
@click.argument('app', required=False)
def health(app):
    conf = DBConfig(app)
    try:
        connect_to_db(conf.url)
        log.info('database available')
    except psycopg2.OperationalError as e:
        log.debug('', exc_info=e)
        print(e)
        raise SystemExit(1)


@root.command()
def ls():
    conf = DBConfig()
    print('\n'.join(list_databases(conf.url)))


@root.command()
@click.argument('app', required=False)
@click.option('--ignore-errors', default=False, help='Continue even if there are errors')
def shell(app, ignore_errors):
    conf = DBConfig(app)
    conf.PGAPPNAME = 'puddl db shell'
    shell_env = os.environ.copy()
    shell_env.update(dict(conf))
    cmd = ['psql']
    if not ignore_errors:
        cmd.extend(['-v', 'ON_ERROR_STOP=1'])
    # want to see good error handling for this kind of thing?
    # https://github.com/pallets/click/blob/19fdc8509a1b946c088512e0e5e388a8d012f0ce/src/click/_termui_impl.py#L472-L487
    return_code = subprocess.Popen(cmd, env=shell_env).wait()
    raise SystemExit(return_code)


@root.command()
@click.argument('app', required=False)
def url(app):
    """
    print DB URL

    Useful for things like this:

        from sqlalchemy import create_engine
        database_url = 'postgresql://puddl:aey1Ki4oaZohseWod2ri@localhost:13370/puddl'
        engine = create_engine(database_url, echo=False)
        df.to_sql('bp', engine)
    """
    db = DB(app)
    print(db.db_config.url)


@root.command()
@click.argument('app', required=False)
@click.option('-E', '--no-export', is_flag=True, help='do not print export')
def env(app, no_export):
    """
    Prints the database's environment.
    WARNING: This dumps your password. Use it like this:

        source <(puddl db env)
    """
    conf = DBConfig(app)
    for k, v in conf.items():
        if no_export:
            print(f'{k}={v}')
        else:
            print(f'export {k}={v}')


@root.command()
@click.argument('app', required=False)
def pastable(app):
    """
    Print database settings in a way that is suited for copy and pasting.
    """
    conf = DBConfig(app)

    human2slot = {
        'Hostname': 'PGHOST',
        'Port': 'PGPORT',
        'Username': 'PGUSER',
        'Password': 'PGPASSWORD',
        'Database': 'PGDATABASE',
        'App': 'PGAPPNAME',
    }

    records = []
    for name, key in human2slot.items():
        value = conf[key]
        records.append(f'  {name}\n{value}\n')

    print('\n'.join(records))


@root.command()
def sessions():
    """
    Lists active sessions.
    """
    conf = DBConfig()
    conf.PGAPPNAME = 'db sessions'
    query = """SELECT pid AS process_id,
           usename AS username,
           datname AS database_name,
           client_addr AS client_address,
           application_name,
           backend_start,
           state,
           state_change
    FROM pg_stat_activity;"""
    click.echo(subprocess.check_output(['psql', '-c', query], encoding='utf-8', env=conf))


@root.command()
@click.argument('old')
@click.argument('new')
def mv(old, new):
    conf = DBConfig()
    query = f"CALL puddl_rename_schema('{old}', '{new}')"
    subprocess.check_call(['psql', '-c', query], env=conf)


@root.command()
@click.argument('app')
def rm(app):
    conf = DBConfig()
    query = f"DROP DATABASE IF EXISTS {app}"
    subprocess.check_call(['psql', '-c', query], env=conf)


def main():
    root(auto_envvar_prefix='PUDDL')


if __name__ == '__main__':
    main()
