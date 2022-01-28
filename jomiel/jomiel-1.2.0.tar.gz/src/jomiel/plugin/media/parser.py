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


class PluginMediaParser(metaclass=ABCMeta):
    """An abstract plugin media parser class.

    Notes:
        - Subclass this when you write a new media parser

    Attributes:
        response (obj): the Response (protobuf) message object to be
            returned to the client

        media (obj): a short-hand for response.media
    """

    __slots__ = ["response", "media"]

    def __init__(self, uri_components):
        """Initializes the object.

        Args:
            uri_components (dict): The parsed URI componenets

        """
        from jomiel.subsys.broker.worker import ResponseBuilder

        (self.response, self.media) = (None, None)

        self.response = ResponseBuilder().response
        self.media = self.response.media

    @abstractmethod
    def parse(self, uri_components):
        """[Override] Parses the relevant metadata for the media.

        Args:
            uri_components (dict): The input URI components

        """

    def __repr__(self):
        """Returns an unambiguous representation of the object."""
        return "Media:\n  response=%s" % self.response


# vim: set ts=4 sw=4 tw=72 expandtab:
