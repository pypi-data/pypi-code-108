# -*- coding: utf-8 -*-
"""
    pip_services3_components.build.IFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for factory components.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any


class IFactory:
    """
    Interface for component factories.

    Factories use locators to identify components to be created.

    The locators are similar to those used to locate components in references.
    They can be of any type like strings or integers. However Pip.Services toolkit
    most often uses Descriptor objects as component locators.
    """

    def can_create(self, locator: Any) -> Any:
        """
        Checks if this factory is able to create component by given locator.

        This method searches for all registered components and returns
        a locator for component it is able to create that matches the given locator.
        If the factory is not able to create a requested component is returns null.

        :param locator: a locator to identify component to be created.

        :return: a locator for a component that the factory is able to create.
        """
        raise NotImplementedError('Method from interface definition')

    def create(self, locator: Any) -> Any:
        """
        Creates a component identified by given locator.

        :param locator: a locator to identify component to be created.

        :return: the created component.
        """
        raise NotImplementedError('Method from interface definition')
