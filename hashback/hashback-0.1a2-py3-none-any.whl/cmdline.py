import json
import logging.config
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import click
from pydantic import BaseSettings

from .algorithms import BackupController
from .local_file_system import LocalFileSystemExplorer
from .log_config import LogConfig, flush_early_logging, setup_early_logging
from .misc import SettingsConfig, register_clean_shutdown, run_then_cancel
from .protocol import Backup, DuplicateBackup, ServerSession

logger = logging.getLogger(__name__)

DATE_FORMAT = click.DateTime(formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'])


@click.group()
@click.option("--config-path", type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=False))
def main(config_path: Optional[Path]):
    setup_early_logging()
    register_clean_shutdown()
    context = click.get_current_context()
    if context.invoked_subcommand == 'configure':
        return
    settings = Settings(config_path=config_path)
    logging.config.dictConfig(settings.logging.dict_config())
    flush_early_logging()
    client = create_client(settings)
    context.call_on_close(lambda: run_then_cancel(client.close()))
    context.obj = client


@main.command('configure')
@click.option('--user/--site', default=True)
@click.option("--config-path", type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=False))
@click.option("--client-id")
@click.option("--database-url")
@click.option("--log-level")
@click.option("--log-unit-level", multiple=True)
@click.option("--credentials")
def configure(config_path: Optional[Path], user: bool, log_level: Optional[str], log_unit_level: List[str],
              credentials: Optional[str], **options):
    if config_path is None:
        config_path = Settings.Config.user_config_path() if user else Settings.Config.site_config_path()

    new_settings = Settings(config_path=config_path, **options)

    # Log levels cannot be passed in or they will unintentionally overwrite instead of amend
    # Besides they exist at a different level.
    if log_level is not None:
        new_settings.logging.log_level = log_level

    for item in log_unit_level:
        log_unit, level = item.split('=', 1)
        new_settings.logging.log_unit_levels = level

    logging.config.dictConfig(new_settings.logging.dict_config())
    flush_early_logging()

    config_path.parent.mkdir(parents=True, exist_ok=True)

    if credentials is not None:
        credentials_path = config_path.parent / 'client-credentials.json'
        logger.info(f"Saving credentials to {credentials_path}")
        credentials_path.unlink(missing_ok=True)
        credentials_path.touch(mode=0o600, exist_ok=False)
        with credentials_path.open('w') as file:
            file.write(credentials)
        new_settings.credentials = credentials_path

    logger.info(f"Saving settings to {config_path}")
    config_path.touch(mode=0o600, exist_ok=True)
    with config_path.open('w') as file:
        file.write(new_settings.json(indent=True, exclude_defaults=True))


@main.command("backup")
@click.option("--timestamp", type=DATE_FORMAT)
@click.option("--description")
@click.option("--overwrite/--no-overwrite", default=False)
@click.option("--fast-unsafe/--slow-safe", default=True)
@click.option("--full-prescan/--low-mem", default=False)
def backup(timestamp: datetime, description: Optional[str], fast_unsafe: bool, full_prescan: bool, overwrite: bool):
    server_session: ServerSession = click.get_current_context().obj
    if timestamp is None:
        timestamp = datetime.now(server_session.client_config.timezone)
    elif timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=server_session.client_config.timezone)

    async def _backup():
        try:
            backup_session = await server_session.start_backup(
                backup_date=timestamp,
                allow_overwrite=overwrite,
                description=description,
            )
        except DuplicateBackup as exc:
            raise click.ClickException(f"Duplicate backup {exc}") from None

        logger.info(f"Backup - {backup_session.config.backup_date}")
        backup_scanner = BackupController(LocalFileSystemExplorer(), backup_session)

        backup_scanner.read_last_backup = fast_unsafe
        backup_scanner.match_meta_only = fast_unsafe
        backup_scanner.full_prescan = full_prescan

        try:
            await backup_scanner.backup_all()
            logger.info("Finalizing backup")
            await backup_session.complete()
            logger.info("All done")
        except:
            logger.warning("Discarding session")
            await backup_session.discard()
            raise

    run_then_cancel(_backup())


@main.command('list')
@click.option("--json/--plain", default=False)
def list_backups(**options):
    client: ServerSession = click.get_current_context().obj

    async def _list():
        logger.info(f"Listing backups for {client.client_config.client_name} ({client.client_config.client_id})")
        tz = client.client_config.timezone
        backups = sorted(((backup_date.astimezone(tz), description)
                          for backup_date, description in await client.list_backups()), key=lambda item: item[0])
        if options['json']:
            result = [{'date_time': backup_date.astimezone(tz).isoformat(), 'description': description}
                      for backup_date, description in backups]
            print(json.dumps(result))
        else:
            if backups:
                print(f"Backup Date/time\tDescription")
                for backup_date, description in backups:
                    print(f"{backup_date}\t{description}")
            else:
                print("No backups found!")

    run_then_cancel(_list())


@main.command()
@click.argument("TIMESTAMP", type=DATE_FORMAT)
@click.option("--json/--plain", default=False)
def describe(timestamp: datetime, **options):
    client: ServerSession = click.get_current_context().obj
    def _timezone_string(t: datetime):
        return t.astimezone(client.client_config.timezone).isoformat()

    async def _describe():
        result: Backup = await client.get_backup(timestamp)
        if options['json']:
            print(result.json())
        else:
            print(f"{_timezone_string(result.backup_date)}: {result.description}")
            print(f"Started: {_timezone_string(result.started)}")
            print(f"Finished: {_timezone_string(result.completed)}")
            print(f"Roots: {[name for name in result.roots.keys()]}")

    run_then_cancel(_describe())


class Settings(BaseSettings):
    config_path: Path = None
    database_url: str
    client_id: str
    credentials: Optional[Path] = None
    logging: LogConfig = LogConfig()

    class Config(SettingsConfig):
        SETTINGS_FILE_DEFAULT_NAME = 'client.json'


def create_client(settings: Settings) -> ServerSession:
    url = urlparse(settings.database_url)
    if url.scheme == '' or url.scheme == 'file':
        return _create_local_client(settings)
    if url.scheme == 'http' or url.scheme =='https':
        return _create_http_client(settings)

    raise ValueError(f"Unknown scheme {url.scheme}")


def _create_local_client(settings: Settings):
    logger.debug("Loading local database plugin")
    # pylint: disable=import-outside-toplevel
    from . import local_database
    return local_database.LocalDatabase(Path(settings.database_url)).open_client_session(settings.client_id)


def _create_http_client(settings: Settings):
    async def _start_session():
        server_version = await client.server_version()
        logger.info(f"Connected to server {server_version.server_type} protocol {server_version.protocol_version}")
        return await ClientSession.create_session(client)

    logger.debug("Loading http client plugin")
    # pylint: disable=import-outside-toplevel
    from . import http_protocol
    from .http_client import ClientSession
    server_properties = http_protocol.ServerProperties.parse_url(settings.database_url)

    if settings.credentials is not None:
        if settings.credentials.is_absolute():
            credentials_path = server_properties.credentials
        else:
            credentials_path = settings.config_path.parent / settings.credentials
        server_properties.credentials = http_protocol.Credentials.parse_file(credentials_path)

    if settings.credentials is None and server_properties.credentials is None:
        from .http_client import RequestsClient
        client = RequestsClient(server_properties)
    else:
        from .basic_auth.client import BasicAuthClient
        client = BasicAuthClient(server_properties)

    session = run_then_cancel(_start_session())
    return session


if __name__ == '__main__':
    main()
