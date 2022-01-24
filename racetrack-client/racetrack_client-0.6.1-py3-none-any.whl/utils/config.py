import os
from pathlib import Path
from typing import List, Type, TypeVar

import dacite
import yaml

from racetrack_client.log.logs import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


def load_config(clazz: Type[T], cast_types: List[Type] = None) -> T:
    """
    Load general configuration from YAML file given in CONFIG_FILE environment var or load default config.
    :param clazz: dataclass config type that should be loaded
    :param cast_types: list of types that should be called to create an instance of a field type from the input data
    :return: configuration object of given "clazz" type
    """
    config_file_path = os.environ.get('CONFIG_FILE')
    if not config_file_path:
        logger.warning('CONFIG_FILE unspecified, loading default config')
        return clazz()

    path = Path(config_file_path)
    if not path.is_file():
        raise FileNotFoundError(f"config file {config_file_path} doesn't exist")

    try:
        with path.open() as file:
            config_dict = yaml.load(file, Loader=yaml.FullLoader)
            config = dacite.from_dict(
                data_class=clazz,
                data=config_dict,
                config=dacite.Config(cast=cast_types or []),
            )

            logger.info(f'config loaded from {config_file_path}: {config}')
            return config
    except Exception as e:
        raise RuntimeError('loading config failed') from e
