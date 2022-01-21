import yaml

import sonusai
from sonusai import logger


def get_default_config() -> dict:
    # Load default config
    try:
        with open(sonusai.mixture.default_config, mode='r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error('Error loading genmixdb default config: {}'.format(e))
        exit()


def get_config_from_file(config_name: str) -> dict:
    config = get_default_config()

    try:
        # Load given config
        with open(config_name, mode='r') as file:
            given_config = yaml.safe_load(file)

        # Use default config as base and overwrite with given config keys as found
        for key in config:
            if key in given_config:
                config[key] = given_config[key]

        return config
    except Exception as e:
        logger.error('Error preparing genmixdb config: {}'.format(e))
        exit()
