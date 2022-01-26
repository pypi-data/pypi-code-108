# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.ContainerReferences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Container references implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.config import IConfigurable
from pip_services3_commons.refer import IReferenceable
from pip_services3_commons.refer import ReferenceException
from pip_services3_commons.reflect import TypeReflector
from pip_services3_components.build import CreateException

from .ManagedReferences import ManagedReferences
from ..config.ContainerConfig import ContainerConfig


class ContainerReferences(ManagedReferences):
    """
    Container managed references that can be created from container configuration.
    """

    def put_from_config(self, config: ContainerConfig):
        """
        Puts components into the references from container configuration.

        :param config: a container configuration with information of components to be added.
        """
        for component_config in config:
            component = None
            locator = None

            try:
                # Create component dynamically
                if component_config.type is not None:
                    locator = component_config.type
                    component = TypeReflector.create_instance_by_descriptor(component_config.type)
                # Or create component statically
                elif component_config.descriptor is not None:
                    locator = component_config.descriptor
                    factory = self._builder.find_factory(locator)
                    component = self._builder.create(locator, factory)
                    if component is None:
                        raise ReferenceException(None, locator)
                    locator = self._builder.clarify_locator(locator, factory)

                # Check that component was created
                if component is None:
                    raise CreateException("CANNOT_CREATE_COMPONENT", "Cannot create component") \
                        .with_details("config", config)

                # Add component to the list
                self._references.put(locator, component)

                # Configure component
                if isinstance(component, IConfigurable):
                    component.configure(component_config.config)

                # Set references to factories
                if isinstance(component, IReferenceable) and hasattr(component, 'can_create') and hasattr(component,
                                                                                                          'create'):
                    component.set_references(self)

            except Exception as ex:
                raise ReferenceException(None, locator).with_cause(ex)
