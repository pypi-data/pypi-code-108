# -*- coding: utf-8 -*-
"""
    pip_services3_components.config.JsonConfigReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    JSON config reader implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import json
import os.path
from typing import Optional, Any

from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.errors.ConfigException import ConfigException
from pip_services3_commons.errors.FileException import FileException

from .FileConfigReader import FileConfigReader


class JsonConfigReader(FileConfigReader):
    """
    Config reader that reads configuration from JSON file.

    The reader supports parameterization using Handlebar template engine.

    ### Configuration parameters ###

        - path:          path to configuration file
        - parameters:    this entire section is used as template parameters
        - ...

    Example:

    .. code-block:: json

        ======== config.json ======
        { "key1": "{{KEY1_VALUE}}", "key2": "{{KEY2_VALUE}}" }
        ===========================

    .. code-block:: python
    
        configReader = JsonConfigReader("config.json")
        parameters = ConfigParams.from_tuples("KEY1_VALUE", 123, "KEY2_VALUE", "ABC")
        configReader.read_config_("123", parameters)
    """

    def __init__(self, path: str = None):
        """
        Creates a new instance of the config reader.

        :param path: (optional) a path to configuration file.
        """
        super(JsonConfigReader, self).__init__(path)

    def read_object_(self, correlation_id: Optional[str], parameters: ConfigParams) -> Any:
        """
        Reads configuration file, parameterizes its content and converts it into JSON object.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param parameters: values to parameters the configuration.

        :return: a JSON object with configuration.
        """
        path = self.get_path()
        if path is None:
            raise ConfigException(correlation_id, "NO_PATH", "Missing config file path")

        if not os.path.isfile(path):
            raise FileException(correlation_id, 'FILE_NOT_FOUND', 'Config file was not found at ' + path)

        try:
            with open(path, 'r') as file:
                config = file.read()
                config = self._parameterize(config, parameters)
                return json.loads(config)
        except Exception as ex:
            raise FileException(
                correlation_id,
                "READ_FAILED",
                "Failed reading configuration " + path + ": " + str(ex)
            ).with_details("path", path).with_cause(ex)

    def read_config_(self, correlation_id: Optional[str], parameters: ConfigParams) -> ConfigParams:
        """
        Reads configuration and parameterize it with given values.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param parameters: values to parameters the configuration or null to skip parameterization.

        :return: ConfigParams configuration.
        """
        value = self.read_object_(correlation_id, parameters)
        return ConfigParams.from_value(value)

    @staticmethod
    def read_object(correlation_id: Optional[str], path: str, parameters: ConfigParams) -> Any:
        """
        Reads configuration file, parameterizes its content and converts it into JSON object.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param path: a path to configuration file.

        :param parameters: values to parameters the configuration.

        :return: a JSON object with configuration.
        """
        return JsonConfigReader(path).read_object_(correlation_id, parameters)

    @staticmethod
    def read_config(correlation_id: Optional[str], path: str, parameters: ConfigParams) -> ConfigParams:
        """
        Reads configuration from a file, parameterize it with given values and returns a new ConfigParams object.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param path: a path to configuration file.

        :param parameters: values to parameters the configuration.

        :return: ConfigParams configuration.
        """
        value = JsonConfigReader(path).read_object_(correlation_id, parameters)
        return ConfigParams.from_value(value)
