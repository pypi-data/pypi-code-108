import logging
import os
import yaml


logger = logging.getLogger(__name__)
config_dir = os.path.dirname(os.path.abspath(__file__))


def read_config(file_name):
    try:
        with open(os.path.join(config_dir, file_name), 'r') as stream:
            return yaml.safe_load(stream)
    except Exception as exc:
        logger.error(exc)
        raise Exception("Unable to parse configuration file")
