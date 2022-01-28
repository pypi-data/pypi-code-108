#
# jomiel
#
# Copyright
#  2019-2020 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from urllib.parse import urlparse

from jomiel.cache import plugin_handlers
from jomiel.error import CannotParseError
from jomiel.error import NoParserError
from jomiel.log import lg
from jomiel.log import log_sanitize_string

NS_NAME = "jomiel.plugin.media"


def script_dispatcher(input_uri):
    """Match input URI to a handling (media) script.

    Args:
        input_uri (string): the input URI to match

    Returns:
        obj: The parsed media meta data in a PluginMediaParser subclass

    Raises:
        NoParserError if no matching handler could not be found

    """
    lg().debug(
        "dispatcher<%s>: match '%s'",
        NS_NAME,
        log_sanitize_string(input_uri),
    )

    (uri_handlers, uri_components) = (
        plugin_handlers[NS_NAME],
        urlparse(input_uri),
    )

    for handler in uri_handlers:
        try:
            # Either return a new subclassed PluginMediaParser object, or
            # raise the CannotParseError exception.
            #
            return handler.inquire(uri_components)
        except CannotParseError:
            # Rinse and repeat until we run out of handlers.
            #
            pass
        except:
            # Fail at all other exceptions by passing the raised
            # exception.
            #
            raise
    # When we run out of handlers, inform the caller that we could
    # not find a matching parser for the given input URI.
    #
    raise NoParserError(
        "Unable to find a matching parser for URI <%s>" % input_uri,
    )


# vim: set ts=4 sw=4 tw=72 expandtab:
