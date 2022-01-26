# -*- coding: utf-8 -*-
"""
    pip_services3_container.refer.ManagedReferences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Managed references implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Sequence, Any, Optional

from pip_services3_commons.refer import References
from pip_services3_commons.run import IOpenable

from .BuildReferencesDecorator import BuildReferencesDecorator
from .LinkReferencesDecorator import LinkReferencesDecorator
from .ReferencesDecorator import ReferencesDecorator
from .RunReferencesDecorator import RunReferencesDecorator


class ManagedReferences(ReferencesDecorator, IOpenable):
    """
    Managed references that in addition to keeping and locating references can also manage their lifecycle:
        - Auto-creation of missing component using available factories
        - Auto-linking newly added components
        - Auto-opening newly added components
        - Auto-closing removed components
    """

    def __init__(self, tuples: Sequence[Any] = None):
        """
        Creates a new instance of the references

        :param tuples: tuples where odd values are component locators (descriptors) and even values are component references
        """
        super(ManagedReferences, self).__init__(None, None)

        self._references: References = References(tuples)
        self._builder: BuildReferencesDecorator = BuildReferencesDecorator(self._references, self)
        self._linker: LinkReferencesDecorator = LinkReferencesDecorator(self._builder, self)
        self._runner: RunReferencesDecorator = RunReferencesDecorator(self._linker, self)

        self.base_references = self._runner

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._linker.is_open() and self._runner.is_open()

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._linker.open(correlation_id)
        self._runner.open(correlation_id)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self._runner.close(correlation_id)
        self._linker.close(correlation_id)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'ManagedReferences':
        """
        Creates a new ManagedReferences object filled with provided key-value pairs called tuples.
        Tuples parameters contain a sequence of locator1, component1, locator2, component2, ... pairs.

        :param tuples: the tuples to fill a new ManagedReferences object.

        :return: a new ManagedReferences object.
        """
        return ManagedReferences(tuples)
