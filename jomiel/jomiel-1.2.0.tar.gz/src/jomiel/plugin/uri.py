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


class PluginURIRefiner(metaclass=ABCMeta):
    """An abstract class

    Notes:
        - Subclass this when you write a new URI refiner

    """

    __slots__ = []

    @abstractmethod
    def refine(self, uri_components):
        """[Override] The handler calls this class method to "demangle"
        the input URI before it sees if it can handle the URI.

        Typically, this means converting shortened URIs, e.g.:
            https://youtu.be/ -> regular youtube video page URI

        Args:
            uri_components (dict): The parsed URI componenets

        Returns:
            dict: The updated URI components

        """

    @abstractmethod
    def compile_regexes(self):
        """[Override] Compiles and caches the regexes used to match and
        modify the input URI.

        """


# vim: set ts=4 sw=4 tw=72 expandtab:
