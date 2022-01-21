"""TODO doc"""

import os
import pkg_resources
import random
import sys
import time

import logging
import logging.handlers

import coloredlogs

from ejerico.sdk.annotations import singleton
from ejerico.sdk.config import ConfigManager

__all__ = ["LoggingManager"]

@singleton
class LoggingManager(object):

    def __init__(self):
        self._config = ConfigManager.instance()
        self._level_name = "INFO"
        self._level = logging._nameToLevel[self._level_name]
        self._format = "{%(asctime)s}[%(levelname)s]: %(message)s"
        self._formatter = logging.Formatter(self._format, datefmt="%Y-%m-%dT%H:%M:%S")
        self._logger = logging.getLogger()


    def boot(self):
        self._level_name = self._config.get("logging_level", default="INFO")
        self._level = logging._nameToLevel[self._level_name]        
        self._logger.setLevel(self._level)
        
        if not self._logger.handlers:
            self._handler = logging.StreamHandler(sys.stdout)                             
            self._handler.setLevel(self._level)                                        
            self._handler.setFormatter(self._formatter)                                        
            self._logger.addHandler(self._handler) 
        
            
        if os.environ.get("EJERICO_DEVELOPMENT_MODE") is not None and bool(os.environ.get("EJERICO_DEVELOPMENT_MODE")):
            coloredlogs.install(logger=self._logger, level=self._level, fmt=self._format)

        
    def getLogger(self):
        return self._logger
