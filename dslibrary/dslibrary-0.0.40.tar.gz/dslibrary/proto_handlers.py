"""
Custom protocol handlers.
"""
import os

from .utils.instantiation import instantiate_class_and_args


class ProtocolHandler(object):
    """
    Base class for protocol-specific handlers.
    """
    def open_resource(self, url: str, mode: str, **kwargs):
        """
        Open a r/w stream to a specific file-like object.
        :param url:         Which file.
        :param mode:        r, rb, w, wb, a, ab
        :param kwargs:      Custom arguments.
        :return:            A file-like object.
        """

    def get_system_connection(self, system_type, uri: str, for_write: bool=False, **kwargs):
        """
        Create a connection to external systems of all types.
        :param system_type:     filesystem, sql, nosql, timeseries, ...
        :param uri:             Base URL for the remote system.
        :param for_write:       Requests write access.
        :param kwargs:          Arguments to help open the connection.
        :return:                See classes in 'engine_intf'.
        """


def load_protocol_handler(url_or_protocol: str, env: dict=None) -> (ProtocolHandler, None):
    """
    Load a protocol handler, given a protocol, or a URL containing a protocol.

    :param url_or_protocol:     Protocol, or a URL containing a protocol, i.e. "myprotocol://hostname/etc."
    :param env:                 Alternate environement.  Uses system environment if not specified.
    """
    if env is None:
        env = os.environ
    # extract protocol
    if "://" in url_or_protocol:
        protocol = url_or_protocol.split("://")[0]
    elif "/" not in url_or_protocol and ":" not in url_or_protocol and " " not in url_or_protocol:
        protocol = url_or_protocol
    else:
        return
    # look up environment variable to see if the given protocol has a special handler
    env_name = f"DSLIBRARY_PROTO_{protocol.upper()}"
    env_val = env.get(env_name)
    if not env_val:
        return
    # look up the referenced handler class and instantiate it
    return instantiate_class_and_args(env_val, ProtocolHandler)
