import copy
import json
import logging
import os
from os import environ

import yaml

from google.protobuf import json_format

from traceableai.config import traceable_config_pb2
from traceableai.config.default import DEFAULT
from traceableai.config.environment import overwrite_with_environment
logger = logging.getLogger(__name__)

class Config(): # pylint:disable=R0903
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.config = build_config()


# We don't want to update a value that is set with an unset value
def merge_config(base_config, overriding_config):
    for key in overriding_config:
        if key in base_config and isinstance(base_config[key], dict):
            if key in overriding_config:
                base_config[key] = merge_config(base_config[key], overriding_config[key])
        else:
            base_config[key] = overriding_config[key]
    return base_config
# Config load ordering
# 1.) Use the defaults
# 2.) Override the defaults with config file
# 3.) Override the config file with env vars
def build_config():
    traceable_config = traceable_config_pb2.AgentConfig()
    config_dict = copy.deepcopy(DEFAULT)
    file_dict = read_from_file()
    if file_dict is not None:
        merge_config(config_dict, file_dict)

    json_string = json.dumps(config_dict)
    logger.debug(json_string)
    json_format.Parse(json_string, traceable_config, ignore_unknown_fields=True)

    overwrite_with_environment(traceable_config)

    return traceable_config

def read_from_file():
    config_path = _config_file_path()
    if config_path is None or not os.path.exists(config_path):
        logger.debug("TA_CONFIG_FILE path not set")
        return None

    with open(config_path, 'r') as config_file:
        try:
            return yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            logger.debug(exc)
            return None

def _config_file_path():
    config_path = environ.get('TA_CONFIG_FILE', None)
    if config_path is None:
        return None
    return config_path
