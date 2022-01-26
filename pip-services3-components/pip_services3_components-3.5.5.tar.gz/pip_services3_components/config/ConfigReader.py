# -*- coding: utf-8 -*-
"""
    pip_services3_components.config.CachedConfigReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Cached config reader implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import abstractmethod
from typing import Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config import IConfigurable
from pip_services3_commons.run import INotifiable

from pip_services3_expressions.mustache import MustacheTemplate

from .IConfigReader import IConfigReader


class ConfigReader(IConfigReader, IConfigurable):
    """
    Abstract config reader that supports configuration parameterization.

    ### Configuration parameters ###
    parameters:            this entire section is used as template parameters
        - ...
    """

    def __init__(self):
        """
        Creates a new instance of the config reader.
        """
        self.__parameters: ConfigParams = ConfigParams()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        parameters = config.get_section("parameters")
        if len(parameters) > 0:
            self.__parameters = parameters

    @abstractmethod
    def read_config_(self, correlation_id: Optional[str], parameters: ConfigParams) -> ConfigParams:
        """
        Reads configuration and parameterize it with given values.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param parameters: values to parameters the configuration or null to skip parameterization.

        :return: ConfigParams configuration.
        """
        raise NotImplementedError('Method is abstract and must be overriden')

    def _parameterize(self, config: str, parameters: ConfigParams) -> str:
        """
        Parameterized configuration template given as string with dynamic parameters.

        :param config: a string with configuration template to be parameterized

        :param parameters: dynamic parameters to inject into the template

        :return: a parameterized configuration string.
        """
        parameters = self.__parameters.override(parameters)
        template = MustacheTemplate(config)

        return template.evaluate_with_variables(parameters)

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
