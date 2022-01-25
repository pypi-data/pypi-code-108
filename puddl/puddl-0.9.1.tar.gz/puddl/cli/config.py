import logging
import os

import click

from puddl.cli.base import root
from puddl.conf import DBConfig, PuddlRC

log = logging.getLogger(__name__)


@root.command()
@click.option('-f', '--force', is_flag=True)
def init(force):
    if PuddlRC.exists():
        if not force:
            raise click.ClickException(f'{PuddlRC.PATH} already exists')
        else:
            log.info(f'forcing overwrite of {PuddlRC.PATH}')
    from dotenv import load_dotenv

    load_dotenv()
    os.environ['PGAPPNAME'] = 'puddl-config init'

    cfg = DBConfig()
    PuddlRC.write(dict(cfg))


@root.command()
def show():
    for k, v in DBConfig().items():
        print(f'{k}={v}')


def main():
    root(auto_envvar_prefix='PUDDL')


if __name__ == '__main__':
    main()
