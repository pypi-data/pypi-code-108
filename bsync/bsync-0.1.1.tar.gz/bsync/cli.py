from pathlib import Path
from getpass import getuser
from contextlib import contextmanager

import click


from bsync.api import BoxAPI
from bsync.sync import BoxSync
from bsync.log import get_logger, LEVELS


USER = getuser()


@contextmanager
def nullcontext(enter_result=None):
    yield enter_result


@click.command()
@click.argument('source_folder_paths', metavar='SOURCE_FOLDER[:PATHS]', envvar='SOURCE_FOLDER',
                type=click.Path(path_type=Path))
@click.argument('box_folder_id', envvar='BOX_FOLDER_ID', type=int)
@click.option('-u', '--box-user', default=USER, envvar='BOX_USER',
              help=f'User account name on Box.com. Defaults to {USER}')
@click.option('-s', '--settings', envvar='BOX_SETTINGS_FILE',
              type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-i', '--ipdb', is_flag=True, help='Drop into ipdb shell on error')
@click.option('-l', '--log-level', type=click.Choice(LEVELS, case_sensitive=False), help='Log level')
@click.option('--log-file', type=click.Path(dir_okay=False, path_type=Path), help='Log file')
@click.option('-o', '--output', type=click.Path(dir_okay=False, path_type=Path),
              help='File to write created items as CSV report')
def bsync(**options):
    """
    Syncs the contents of local folder to your Box account

    SOURCE_FOLDER is the path of an existing local folder.
    Additional, optional PATHS can be added as a glob expression after the folder.

    BOX_FOLDER_ID is the ID for the folder in Box where you want the files sent

    Example:

        bsync -s 12345.json -l DEBUG images:*.jpg 123456789
    """
    ctx = nullcontext
    if options['ipdb']:
        from ipdb import launch_ipdb_on_exception
        ctx = launch_ipdb_on_exception
    with ctx():
        logger = get_logger(options)
        api = BoxAPI(options, logger)
        bsync = BoxSync(options, api, logger)
        bsync()
        if options['output']:
            bsync.output(options['output'])
