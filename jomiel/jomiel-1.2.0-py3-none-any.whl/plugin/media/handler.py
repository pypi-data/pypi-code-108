#
# jomiel
#
# Copyright
#  2019 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from abc import ABCMeta
from abc import abstractmethod


class PluginMediaHandler(metaclass=ABCMeta):
    """An abstract class.

    Notes:
        - Subclass this when you write a new URI handler

    """

    __slots__ = []

    @abstractmethod
    def inquire(self, uri_components):
        """Called to determine whether the given (input) URI can be
        handled by the handler.

        Args:
            uri_components (dict): The input URI components

        Returns:
            obj: A subclass of PluginMediaParser

        Raises:
            CannotParseError, if the object cannot handle the URI

        """

    @abstractmethod
    def can_parse(self, uri_components):
        """[Override] Determines whether the given input URI can be
        handled.

        Args:
            uri_components (dict): The input URI components

        Returns:
            bool: True if the given input URI can be handled

        Notes:
            - Do NOT call this method, call `inquire', instead

        """

    @abstractmethod
    def compile_regexes(self):
        """[Override] Compiles and caches the regexes used to match the
        URI.

        """


# vim: set ts=4 sw=4 tw=72 expandtab:
