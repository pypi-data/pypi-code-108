# -*- coding: utf-8 -*-
"""
    pip_services3_components.config.MemoryConfigReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Memory config reader implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable
from pip_services3_commons.run import INotifiable
from pip_services3_expressions.mustache.MustacheTemplate import MustacheTemplate

from .IConfigReader import IConfigReader


class MemoryConfigReader(IConfigReader, IReconfigurable):
    """
    Config reader that stores configuration in memory.

    ### Configuration parameters ###

        The configuration parameters are the configuration template

    Example:

    .. code-block:: python
    
        config = ConfigParams.from_tuples(
	                "connection.host", "localhost",
	                "connection.port", "8080"
                )

        configReader = MemoryConfigReader()
        configReader.configure(config)

        parameters = ConfigParams.fromValue(os.get_env())
        configReader.read_config_("123", parameters)
    """

    def __init__(self, config: ConfigParams = None):
        """
        Creates a new instance of config reader.

        :param config: (optional) component configuration parameters
        """
        self._config: ConfigParams = config or ConfigParams()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._config = config

    def read_config_(self, correlation_id: Optional[str], parameters: ConfigParams) -> ConfigParams:
        """
        Reads configuration and parameterize it with given values.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param parameters: values to parameters the configuration or null to skip parameterization.

        :return: ConfigParams configuration.
        """
        if parameters is not None:
            config = ConfigParams(self._config).to_string()
            template = MustacheTemplate(config)
            config = template.evaluate_with_variables(parameters)
            return ConfigParams.from_string(config)
        else:
            return ConfigParams(self._config)

    def add_change_listener(self, listener: INotifiable):
        """
        Adds a listener that will be notified when configuration is changed

        :param listener: a listener to be added.
        """
        # Do nothing...

    def remove_change_listener(self, listener: INotifiable):
        """
        Remove a previously added change listener.

        :param listener: a listener to be removed.
        """
        # Do nothing...
