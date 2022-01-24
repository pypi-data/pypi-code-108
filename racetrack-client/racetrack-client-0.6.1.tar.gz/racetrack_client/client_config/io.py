import dataclasses
from pathlib import Path
from typing import Dict, Optional

import dacite
import yaml
from racetrack_client.log.context_error import wrap_context
from racetrack_client.client_config.client_config import ClientConfig, Credentials
from racetrack_client.log.logs import get_logger

logger = get_logger(__name__)


def load_client_config() -> ClientConfig:
    """Load global options for a local client"""
    path = Path.home() / '.racetrack' / 'config.yaml'
    if not path.is_file():
        return ClientConfig()

    try:
        with path.open() as file:
            config_dict = yaml.load(file, Loader=yaml.FullLoader)
            config = dacite.from_dict(
                data_class=ClientConfig,
                data=config_dict,
                config=dacite.Config(cast=[]),
            )

            logger.info(f'client config loaded from {path}')
            return config
    except Exception as e:
        raise RuntimeError('loading client config failed') from e


def load_credentials_from_dict(credentials_dict: Optional[Dict]) -> Optional[Credentials]:
    if credentials_dict is None:
        return None

    with wrap_context('parsing credentials'):
        return dacite.from_dict(
            data_class=Credentials,
            data=credentials_dict,
            config=dacite.Config(cast=[]),
        )


def save_client_config(config: ClientConfig):
    data_dict = dataclasses.asdict(config)

    dir_path = Path.home() / '.racetrack'
    dir_path.mkdir(parents=True, exist_ok=True)
    config_path = dir_path / 'config.yaml'

    with open(config_path, 'w') as outfile:
        yaml.dump(data_dict, outfile)
