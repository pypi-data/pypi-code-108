# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.LinkReferencesDecorator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Link references decorator implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from pip_services3_commons.refer import IReferences
from pip_services3_commons.refer import Referencer
from pip_services3_commons.run import IOpenable

from .ReferencesDecorator import ReferencesDecorator


class LinkReferencesDecorator(ReferencesDecorator, IOpenable):
    """
    References decorator that automatically sets references to newly added components
    that implement :class:`IReferenceable <pip_services3_commons.refer.IReferenceable.IReferenceable>` interface and unsets references
    from removed components that implement :class:`IUnreferenceable <pip_services3_commons.refer.IUnreferenceable.IUnreferenceable>` interface.
    """

    def __init__(self, next_references: IReferences, top_references: IReferences):
        """
        Creates a new instance of the decorator.

        :param next_references: the next references or decorator in the chain.

        :param top_references: the decorator at the top of the chain.
        """
        super(LinkReferencesDecorator, self).__init__(next_references, top_references)
        self.__opened = False

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if not self.__opened:
            components = self.get_all()
            Referencer.set_references(self.parent_references, components)
            self.__opened = True

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.__opened:
            components = self.get_all()
            Referencer.unset_references(components)
            self.__opened = False

    def put(self, locator: Any = None, component: Any = None) -> Any:
        """
        Puts a new component into this component map.

        :param locator: a locator to find the component by.

        :param component: a component component to be added.
        """
        super(LinkReferencesDecorator, self).put(locator, component)

        if self.__opened:
            Referencer.set_references_for_one(self.parent_references, component)

    def remove(self, locator: Any) -> Any:
        """
        Removes a previously added component that matches specified locator.
        If many references match the locator, it removes only the first one.
        When all references shall be removed, use :func:`remove_all` method instead.

        :param locator: a locator to remove component

        :return: the removed component component.
        """
        component = super(LinkReferencesDecorator, self).remove(locator)

        if self.__opened:
            Referencer.unset_references_for_one(component)

        return component

    def remove_all(self, locator: Any) -> List[Any]:
        """
        Removes all component references that match the specified locator.

        :param locator: the locator to remove references by.

        :return: a list, containing all removed references.
        """
        components = super(LinkReferencesDecorator, self).remove_all(locator)

        if self.__opened:
            Referencer.unset_references(components)

        return components
