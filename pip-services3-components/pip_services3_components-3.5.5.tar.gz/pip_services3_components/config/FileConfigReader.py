# -*- coding: utf-8 -*-
"""
    pip_services3_components.config.FileConfigReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    File config reader implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.config.ConfigParams import ConfigParams

from .ConfigReader import ConfigReader


class FileConfigReader(ConfigReader):
    """
    Abstract config reader that reads configuration from a file.
    Child classes add support for config files in their specific format
    like JSON, YAML or property files.

    ### Configuration parameters ###
        - path:          path to configuration file
        - parameters:    this entire section is used as template parameters
        - ...
    """

    def __init__(self, path: str = None):
        """
        Creates a new instance of the config reader.

        :param path: (optional) a path to configuration file.
        """
        super(FileConfigReader, self).__init__()
        self.__path: str = path

    def get_path(self) -> str:
        """
        Get the path to configuration file.

        :return: the path to configuration file.
        """
        return self.__path

    def set_path(self, path: str):
        """
        Set the path to configuration file.

        :param path: a new path to configuration file.
        """
        self.__path = path

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super(FileConfigReader, self).configure(config)
        self.__path = config.get_as_string_with_default("path", self.__path)
