import logging.config
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import click
from pydantic import BaseSettings, root_validator
from uvicorn import run

from . import basic_auth
from ..http_protocol import Credentials, DEFAULT_PORT
from ..local_database import LocalDatabase
from ..log_config import LogConfig, flush_early_logging, setup_early_logging
from ..misc import SettingsConfig, register_clean_shutdown
from ..server import app

logger = logging.getLogger(__name__)


@click.group()
@click.option("--config-path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def main(context: click.Context, config_path: Path):
    setup_early_logging()
    settings = Settings(config_path=config_path)
    context.obj = settings


@main.command()
@click.option("--host", default=["::1", "127.0.0.1"], multiple=True)
@click.option("--port", type=click.INT, default=8000)
def run_foreground(host: List[str], port: int):
    settings: Settings = click.get_current_context().obj
    log_config = configure_logging(settings)

    database = LocalDatabase(settings.database_path)
    authorizer = basic_auth.BasicAuthenticatorAuthorizer(basic_auth.BasicAuthDb(settings.users_path))
    app.configure(authorizer, database)

    register_clean_shutdown()
    logging.info("Starting up")
    run(f"{app.__name__}:app", access_log=True, log_config=log_config, host=host, port=port)


@main.command()
@click.argument('CLIENT')
@click.argument('CLIENT_PASSWORD', required=False)
@click.option('--display-credentials/--hide-credentials', default=False)
def authorize(client: str, client_password: Optional[str], display_credentials:bool):
    settings: Settings = click.get_current_context().obj
    logging.config.dictConfig(settings.logging.dict_config())
    flush_early_logging()

    users_db = basic_auth.BasicAuthDb(auth_file=settings.users_path)
    if client_password is None:
        display_credentials = True
        client_password = str(uuid4())

    device_db = LocalDatabase(settings.database_path)
    client_config = device_db.open_client_session(client_id_or_name=client).client_config

    logger.info(f"Authorizing Client: {client_config.client_name} ({client_config.client_id})")
    if display_credentials:
        credentials = Credentials(
            auth_type='basic',
            username=str(client_config.client_id),
            password=client_password,
        )
        token = credentials.json(exclude_defaults=True)
        logger.info(f"Credentials for {client}: \n{token}")

    users_db.register_user(username=str(client_config.client_id), password=client_password)


@main.command()
@click.argument('CLIENT')
def revoke(client: str):
    settings: Settings = click.get_current_context().obj
    logging.config.dictConfig(settings.logging.dict_config())
    flush_early_logging()

    device_db = LocalDatabase(settings.database_path)
    client_config = device_db.open_client_session(client_id_or_name=client).client_config

    users_db = basic_auth.BasicAuthDb(auth_file=settings.users_path)
    logger.info(f"Revoking Client: {client_config.client_name} ({client_config.client_id})")

    users_db.unregister_user(username=str(client_config.client_id))


class Settings(BaseSettings):
    config_path: Path
    database_path: Path
    users_path: Path
    session_cache_size: int = 128
    port: int = DEFAULT_PORT
    host: str = "localhost"
    logging: LogConfig = LogConfig()

    class Config(SettingsConfig):
        SETTINGS_FILE_DEFAULT_NAME = 'basic-server.json'

    # pylint: disable=no-self-argument,no-self-use
    @root_validator
    def _relative_path(cls, values: Dict[str, Any]):
        for item in 'database_path', 'users_path':
            if item in values and not values[item].is_absolute():
                values[item] = values['config_path'].parent / values[item]
        return values


def configure_logging(settings: Settings) -> Dict[str, Any]:
    from uvicorn.config import LOGGING_CONFIG
    log_config = LOGGING_CONFIG.copy()
    del log_config['loggers']['uvicorn']['handlers']
    log_config = settings.logging.dict_config(base_logger_dict=log_config)
    logging.config.dictConfig(log_config)
    flush_early_logging()
    return log_config


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
