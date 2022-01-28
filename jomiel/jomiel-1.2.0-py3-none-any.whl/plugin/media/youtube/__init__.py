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
from jomiel.error import CannotParseError
from jomiel.plugin.media.handler import PluginMediaHandler
from jomiel.plugin.media.youtube.parser import Parser
from jomiel.plugin.media.youtube.uri import URIRefiner


class Handler(PluginMediaHandler):
    """Media handler implementation for YouTube."""

    __slots__ = ["name", "regex", "refiner"]

    def __init__(self):
        """Initializes the object."""
        super().__init__()
        self.refiner = URIRefiner()
        self.compile_regexes()
        self.name = __name__

    def inquire(self, uri_components):
        """Called to determine whether the given (input) URI can be
        handled by the handler.

        Args:
            uri_components (dict): The input URI components

        Returns:
            obj: a new parser instance

        Raises:
            CannotParseError, if the object cannot handle the URI

        """
        uri_components = self.refiner.refine(uri_components)

        if not self.can_parse(uri_components):
            raise CannotParseError

        return Parser(uri_components)

    def can_parse(self, uri_components):
        """[Override] Determines whether the given input URI can be
        handled.

        Args:
            uri_components (dict): The input URI components

        Returns:
            bool: True if the given input URI can be handled

        Notes:
            - Do NOT  call this method, call `inquire', instead

        """
        uri = uri_components
        return (
            self.regex["scheme"].match(uri.scheme)
            and self.regex["netloc"].search(uri.netloc.lower())
            and self.regex["query"].search(uri.query.lower())
            and self.regex["path"].match(uri.path.lower())
        )

    def compile_regexes(self):
        """Compiles and caches the regexes used to match the URI."""
        from re import compile as rxc

        self.regex = {
            "scheme": rxc(r"https?$"),
            "netloc": rxc(r"youtube\.com$"),
            "query": rxc(r"v=[\w\-_]{11}"),
            "path": rxc(r"/watch$"),
        }


# vim: set ts=4 sw=4 tw=72 expandtab:
