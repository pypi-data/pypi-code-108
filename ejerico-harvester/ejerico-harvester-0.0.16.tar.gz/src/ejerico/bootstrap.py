"""
TODO doc
"""
import os
import sys
import logging
import pathlib

from pkg_resources import get_distribution, resource_filename
from pathlib import Path

from ejerico.sdk.config import ConfigManager
from ejerico.sdk.logging import LoggingManager
from ejerico.sdk.stat import StatManager
from ejerico.sdk.annotations import singleton

__all__ = ["Bootstrap"]
__version__ = get_distribution("ejerico-harvester").version

@singleton
class Bootstrap(object):

    def __init__(self):
        self.config = None
        self.home = None

    def boot(self, arguments):
        self.config = ConfigManager.instance()
        #self.config.configURL = arguments.config_url
        #self.config.configUSERNAME = arguments.config_username
        #self.config.configPASSWORD = arguments.config_password
        #self.config.configTOKEN = arguments.config_token
        self.config.configPATH = arguments.config_path
        self.config.boot()

        self.home = "{}{}.ejerico".format(str(pathlib.Path.home()), os.sep)

        self.logging = LoggingManager.instance()
        self.logging.boot()
        
        self.stat= StatManager.instance()
        self.stat.boot()

    def __get_logging_level(self):
        logging_levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }

        my_level = self.config.get("logging_level", default="UNKNOWN")
        my_level = my_level.strip().upper()
        return logging_levels[my_level] if my_level in logging_levels else logging.INFO
            
        return


