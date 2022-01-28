import logging
from pathlib import Path

import click

from .. import protocol
from ..local_database import LocalDatabase, Configuration
from ..misc import register_clean_shutdown
from ..log_config import setup_logging

logger = logging.getLogger(__name__)


def main():
    register_clean_shutdown()
    setup_logging()
    # pylint: disable=no-value-for-parameter
    click_main()


@click.group()
@click.argument("DATABASE", type=click.Path(path_type=Path, file_okay=False), envvar="BACKUP_DATABASE")
@click.pass_context
def click_main(ctx: click.Context, database: Path):
    if ctx.invoked_subcommand != 'create':
        ctx.obj = LocalDatabase(database)
    else:
        ctx.obj = database


@click_main.command('create')
@click.option("--backup-by", type=click.Choice(['date', 'timestamp'], case_sensitive=False), default="date")
@click.option("--friendly-links/--flat", default=True)
@click.option("--store-split-count", type=click.INT, default=2)
@click.pass_obj
def create(database: Path, **db_config):
    config = Configuration(**db_config)
    logger.info("Creating database %s", database)
    LocalDatabase.create_database(base_path=database, configuration=config)


@click_main.command('add-client')
@click.argument('CLIENT_NAME', envvar="CLIENT_NAME")
@click.pass_obj
def add_client(database: LocalDatabase, client_name: str):
    if not client_name:
        logger.warning("No GROUP_NAME specified.  Nothing to do.")

    config = protocol.ClientConfiguration(
        client_name=client_name,
    )
    database.create_client(config)
    logger.info("Created client %s", config.client_id)


@click_main.command('add-directory')
@click.argument('CLIENT_NAME', envvar="CLIENT_NAME")
@click.argument('ROOT_NAME')
@click.argument('ROOT_PATH', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--include', type=click.Path(path_type=Path), multiple=True)
@click.option('--exclude', type=click.Path(path_type=Path), multiple=True)
@click.pass_obj
def add_root(database: LocalDatabase, client_name: str, root_name: str, root_path: Path, **options):
    def normalize(path: Path) -> str:
        if path.is_absolute():
            return str(path.relative_to(root_path))
        return str(path)

    # Normalize paths correctly
    root_path = Path(root_path).absolute()
    include = [normalize(path) for path in options['include']]
    exclude = [normalize(path) for path in options['exclude']]
    root_path = str(root_path)

    client = database.open_client_session(client_id_or_name=client_name)
    new_dir = protocol.ClientConfiguredBackupDirectory(base_path=root_path)
    for path in include:
        new_dir.filters.append(protocol.Filter(filter=protocol.FilterType.INCLUDE, path=path))
    for path in exclude:
        new_dir.filters.append(protocol.Filter(filter=protocol.FilterType.EXCLUDE, path=path))
    client.client_config.backup_directories[root_name] = new_dir
    client.save_config()
