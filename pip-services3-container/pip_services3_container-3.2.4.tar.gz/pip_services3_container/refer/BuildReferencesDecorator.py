# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.BuildReferencesDecorator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Build references decorator implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional, List

from pip_services3_commons.refer import Descriptor
from pip_services3_commons.refer import IReferences
from pip_services3_commons.refer import ReferenceException
from pip_services3_components.build import IFactory

from .ReferencesDecorator import ReferencesDecorator


class BuildReferencesDecorator(ReferencesDecorator):
    """
    References decorator that automatically creates missing components using
    available component factories upon component retrival.
    """

    def __init__(self, next_references: IReferences, top_references: IReferences):
        """
        Creates a new instance of the decorator.

        :param next_references: the next references or decorator in the chain.

        :param top_references: the decorator at the top of the chain.
        """
        super(BuildReferencesDecorator, self).__init__(next_references, top_references)

    def find_factory(self, locator: Any) -> Optional[IFactory]:
        """
        Finds a factory capable creating component by given descriptor
        from the components registered in the references.

        :param locator: a locator of component to be created.

        :return: found factory or null if factory was not found.
        """
        components = self.get_all()
        for component in components:
            if isinstance(component, IFactory):
                if component.can_create(locator) is not None:
                    return component
        return None

    def create(self, locator: Any, factory: IFactory) -> Any:
        """
        Creates a component identified by given locator.

        :param locator: a locator to identify component to be created.

        :param factory: a factory that shall create the component.

        :return: the created component.
        """
        if factory is None:
            return None

        try:
            # Create component
            return factory.create(locator)
        except Exception as ex:
            return None

    def clarify_locator(self, locator: Any, factory: IFactory) -> Any:
        """
        Clarifies a component locator by merging two descriptors into one to replace missing fields.
        That allows to get a more complete descriptor that includes all possible fields.

        :param locator: a component locator to clarify.

        :param factory: a factory that shall create the component.

        :return: clarified component descriptor (locator)
        """
        if factory is None:
            return locator
        if not isinstance(locator, Descriptor):
            return locator

        another_locator = factory.can_create(locator)
        if another_locator is None:
            return locator
        if not isinstance(another_locator, Descriptor):
            return locator

        descriptor = locator
        another_descriptor = another_locator

        return Descriptor(
            descriptor.get_group() if descriptor.get_group() != None else another_descriptor.get_group(),
            descriptor.get_type() if descriptor.get_type() != None else another_descriptor.get_type(),
            descriptor.get_kind() if descriptor.get_kind() != None else another_descriptor.get_kind(),
            descriptor.get_name() if descriptor.get_name() != None else another_descriptor.get_name(),
            descriptor.get_version() if descriptor.get_version() != None else another_descriptor.get_version()
        )

    def find(self, locator: Any, required: bool) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find a component by.

        :param required: forces to raise an exception if no component is found.

        :return: a list with matching component references.
        """
        components = super(BuildReferencesDecorator, self).find(locator, False)

        # Try to create component
        if len(components) == 0:
            factory = self.find_factory(locator)
            component = self.create(locator, factory)
            if component is not None:
                try:
                    locator = self.clarify_locator(locator, factory)
                    self.parent_references.put(locator, component)
                    components.append(component)
                except Exception as ex:
                    # Ignore exception
                    pass

        # Throw exception is no required components found
        if required and len(components) == 0:
            raise ReferenceException(None, locator)

        return components
