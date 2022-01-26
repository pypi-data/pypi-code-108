# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.ReferencesDecorator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    References decorator implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from pip_services3_commons.refer import IReferences


class ReferencesDecorator(IReferences):
    """
    Chainable decorator for :class:`IReferences <pip_services3_commons.refer.IReferences>` that allows to inject additional capabilities
    such as automatic component creation, automatic registration and opening.
    """

    def get_one_before(self, reference, locator):
        pass

    def __init__(self, next_references: Optional[IReferences], top_references: Optional[IReferences]):
        """
        Creates a new instance of the decorator.

        :param next_references: the next references or decorator in the chain.

        :param top_references: the decorator at the top of the chain.
        """
        # The next references or decorator in the chain.
        self.base_references: IReferences = next_references if next_references is not None else top_references
        # The decorator at the top of the chain.
        self.parent_references: IReferences = top_references if top_references is not None else next_references

    def put(self, locator: Any = None, component: Any = None):
        """
        Puts a new reference into this reference map.

        :param locator: a locator to find the reference by.
        :param component: a component reference to be added.
        """
        self.base_references.put(locator, component)

    def remove(self, locator: Any) -> Any:
        """
        Removes a previously added component that matches specified locator.
        If many references match the locator, it removes only the first one.
        When all references shall be removed, use :func:`remove_all` method instead.

        :param locator: a locator to remove component

        :return: the removed component component.
        """
        return self.base_references.remove(locator)

    def remove_all(self, locator: Any) -> List[Any]:
        """
        Removes all component references that match the specified locator.

        :param locator: the locator to remove references by.

        :return: a list, containing all removed references.
        """
        return self.base_references.remove_all(locator)

    def get_all_locators(self) -> List[Any]:
        """
        Gets locators for all registered component references in this component map.

        :return: a list with component locators.
        """
        return self.base_references.get_all_locators()

    def get_all(self) -> List[Any]:
        """
        Gets all component references registered in this component map.

        :return: a list with component references.
        """
        return self.base_references.get_all()

    def get_one_optional(self, locator: Any) -> Any:
        """
        Gets an optional component component that matches specified locator.

        :param locator: the locator to find references by.

        :return: a matching component component or null if nothing was found.
        """
        try:
            components = self.find(locator, False)
            return components[0] if len(components) > 0 else None
        except Exception as ex:
            return None

    def get_one_required(self, locator: Any) -> Any:
        """
        Gets a required component component that matches specified locator.

        :param locator: the locator to find a component by.

        :return: a matching component component.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
        """
        components = self.find(locator, True)
        return components[0] if len(components) > 0 else None

    def get_optional(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find references by.

        :return: a list with matching component references or empty list if nothing was found.
        """
        try:
            return self.find(locator, False)
        except Exception as ex:
            return []

    def get_required(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.
        At least one component component must be present. If it doesn't the method throws an error.

        :param locator: the locator to find references by.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
        """
        return self.find(locator, True)

    def find(self, locator: Any, required: bool) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find a component by.

        :param required: forces to raise an exception if no component is found.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when required is set to true but no references found.
        """
        return self.base_references.find(locator, required)
