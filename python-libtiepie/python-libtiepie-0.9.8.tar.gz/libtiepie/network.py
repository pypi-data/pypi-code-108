from ctypes import *
from .api import api
from .const import *
from .library import library
from .networkservers import NetworkServers


class Network(object):
    """"""

    def __init__(self):
        self._servers = NetworkServers()

    def _get_servers(self):
        return self._servers

    def _get_auto_detect_enabled(self):
        """ Check whether automatically detecting network instruments and instrument servers is enabled. """
        value = api.NetGetAutoDetectEnabled()
        library.check_last_status_raise_on_error()
        return value != BOOL8_FALSE

    def _set_auto_detect_enabled(self, value):
        value = BOOL8_TRUE if value else BOOL8_FALSE
        api.NetSetAutoDetectEnabled(value)
        library.check_last_status_raise_on_error()

    auto_detect_enabled = property(_get_auto_detect_enabled, _set_auto_detect_enabled)
    servers = property(_get_servers)


network = Network()
