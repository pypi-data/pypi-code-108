import logging
import os
import yaml
from kortical.api.code import Code


logger = logging.getLogger(__name__)
config_dir = os.path.dirname(os.path.abspath(__file__))


def read_config(file_name):
    try:
        with open(os.path.join(config_dir, file_name), 'r') as stream:
            return yaml.safe_load(stream)
    except Exception as exc:
        logger.error(exc)
        raise Exception("Unable to parse configuration file")


def read_model_code(file_name):
    try:
        return Code.from_file(os.path.join(config_dir, file_name))
    except Exception as exc:
        logger.error(exc)
        raise Exception("Unable to parse configuration file")