from komora_syncer import __appname__

import os
import appdirs
import yaml

import configparser
import logging
logger = logging.getLogger(__name__)

os.environ["XDG_CONFIG_DIRS"] = "/etc"
CONFIG_DIRS = (
    appdirs.user_config_dir(__appname__),
    appdirs.site_config_dir(__appname__),
)
CONFIG_FILENAME = "config.yml"
LOGGING_FILENAME = "logging.ini"


def get_config():
    """
    Get config file and load it with yaml
    :returns: loaded config in yaml, as a dict object
    """
    if getattr(get_config, "cache", None):
        return get_config.cache

    if os.environ.get("CONFIG_FOLDER_PATH"):
        config_path = os.path.join(os.environ["CONFIG_FOLDER_PATH"], CONFIG_FILENAME)
    else:
        for d in CONFIG_DIRS:
            config_path = os.path.join(d, CONFIG_FILENAME)
            if os.path.isfile(config_path):
                break
    try:
        with open(config_path, "r") as config_file:
            conf = yaml.safe_load(config_file)
            get_config.cache = conf
            return conf
    except FileNotFoundError as e:
        logger.debug(e)
        if os.environ.get("CONFIG_FOLDER_PATH"):
            logger.error(
                "Configuration file {} not found.".format(
                    os.environ["CONFIG_FOLDER_PATH"]
                )
            )
        else:
            logger.error(
                "No configuration file can be found. Please create a "
                "config.yml in one of these directories:\n"
                "{}".format(", ".join(CONFIG_DIRS))
            )
        raise FileNotFoundError


def get_logging_path():
    """
    Get logging.ini file path
    :returns: path to logging.ini file
    """

    if os.environ.get("CONFIG_FOLDER_PATH"):
        log_conf_path = os.path.join(os.environ.get(
            "CONFIG_FOLDER_PATH"), LOGGING_FILENAME)
    else:
        for d in CONFIG_DIRS:
            log_conf_path = os.path.join(d, LOGGING_FILENAME)
            if os.path.isfile(log_conf_path):
                break

    try:
        with open(log_conf_path, "r") as log_file:
            return log_conf_path
    except FileNotFoundError as e:
        logger.debug(e)
        if os.environ.get("CONFIG_FOLDER_PATH"):
            logger.error(
                "Configuration file {} not found.".format(
                    log_conf_path
                )
            )
        else:
            logger.error(
                "No logging configuration file can be found. Please create a "
                "logging.ini in one of these directories:\n"
                "{}".format(", ".join(CONFIG_DIRS))
            )
        raise FileNotFoundError


class LoggingConfig():
    def __init__(self):
        super().__init__()
        self._config = LoggingConfig.load_config()

    def load_config():
        log_conf_file = get_logging_path()
        config = configparser.ConfigParser()

        try:
            if config.read(log_conf_file):
                pass
            else:
                raise FileNotFoundError
        except FileNotFoundError as e:
            logger.exception(f"Unable to open file {log_conf_file}")
            raise

        return config
