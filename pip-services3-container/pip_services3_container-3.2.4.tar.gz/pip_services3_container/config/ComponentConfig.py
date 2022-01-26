# -*- coding: utf-8 -*-
"""
    pip_services3_container.config.ComponentConfig
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Component configuration implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import Descriptor
from pip_services3_commons.reflect import TypeDescriptor


class ComponentConfig:
    """
    Configuration of a component inside a container.

    The configuration includes type information or descriptor, and component configuration parameters.
    """

    def __init__(self, descriptor: Descriptor = None, type: TypeDescriptor = None, config: ConfigParams = None):
        """
        Creates a new instance of the component configuration.

        :param descriptor: (optional) a components descriptor (locator).

        :param type: (optional) a components type descriptor.

        :param config: (optional) component configuration parameters.
        """
        self.descriptor: Descriptor = descriptor
        self.type: TypeDescriptor = type
        self.config: ConfigParams = config

    @staticmethod
    def from_config(config: ConfigParams) -> 'ComponentConfig':
        """
        Creates a new instance of ComponentConfig based on section from container configuration.

        :param config: component parameters from container configuration

        :return: a newly created ComponentConfig
        """
        descriptor = Descriptor.from_string(config.get_as_nullable_string("descriptor"))
        type = TypeDescriptor.from_string(config.get_as_nullable_string("type"))

        if descriptor is None and type is None:
            raise ConfigException(None, "BAD_CONFIG", "Component configuration must have descriptor or type")

        return ComponentConfig(descriptor, type, config)
