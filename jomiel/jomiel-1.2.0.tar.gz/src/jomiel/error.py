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


class BaseError(Exception):
    """Base class for jomiel-specific exceptions

    Attributes:
        message (str): explanation of the error

    """

    __slots__ = ["message"]

    def __init__(self, message=None):
        super().__init__()
        self.message = message if message else ""


class InvalidInputError(BaseError):
    """Validation failed for the given URI.

    Broker validates the given input URI before passing it to the plugin
    handlers. If the validation fails, this error is raised.

    """


class NoParserError(BaseError):
    """Failed to find a parser for the given URI.

    Dispatcher for handlers raises this if it was unable to locate a
    matching handler for the input URI.

    """


class CannotParseError(BaseError):
    """Parser was unable to handle the given input URI.

    The handlers raise this exception to signal that they were unable to
    handle the given input URI.

    This normally caught by the dispatcher for the handlers. It will
    then move on the next handler in the list.

    """


class ParseError(BaseError):
    """Failed and/or unable to parse a meta data property.

    Or -- something else went wrong while parsing meta data.

    This is a "general purpose error", used to relay a more descriptive
    explanation of the error to the caller.

    """


# vim: set ts=4 sw=4 tw=72 expandtab:
