# -*- coding: utf-8 -*-
"""
    pip_services3_container.config.ContainerConfig
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Container configuration implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Sequence, Any

from pip_services3_commons.config import ConfigParams

from .ComponentConfig import ComponentConfig


class ContainerConfig(list):
    """
    Container configuration defined as a list of component configurations.
    """

    def __init__(self, components: Sequence[ComponentConfig] = None):
        """
        Creates a new instance of container configuration.

        :param components: (optional) a list of component configurations.
        """
        super(ContainerConfig, self).__init__()
        if components is not None:
            for component in components:
                self.append(component)

    @staticmethod
    def from_value(value: Any) -> 'ContainerConfig':
        """
        Creates a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>` object filled with key-value pairs from specified object.
        The value is converted into :class:`ConfigParams <pip_services3_commons.config.ConfigParams.ConfigParams>` object which is used to create the object.

        :param value: an object with key-value pairs used to initialize a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>`.

        :return: a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>` object.
        """
        config = ConfigParams.from_value(value)
        return ContainerConfig.from_config(config)

    @staticmethod
    def from_config(config: ConfigParams) -> 'ContainerConfig':
        """
        Creates a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>` object based on configuration parameters.
        Each section in the configuration parameters is converted into a component configuration.

        :param config: an object with key-value pairs used to initialize a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>`.

        :return: a new :class:`ContainerConfig <pip_services3_container.config.ContainerConfig.ContainerConfig>` object.
        """
        result = ContainerConfig()
        if config is None:
            return result

        for section in config.get_section_names():
            component_config = config.get_section(section)
            result.append(ComponentConfig.from_config(component_config))

        return result
