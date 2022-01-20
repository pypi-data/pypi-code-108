import sys
import re

from ._ingenialink import lib


DIST_FRAME_SIZE_BYTES = 128
DIST_FRAME_SIZE = 512
SINGLE_AXIS_MINIMUM_SUBNODES = 2

DEFAULT_MESSAGE_RETRIES = 7
DEFAULT_MESSAGE_TIMEOUT = 200

DEFAULT_PDS_TIMEOUT = 1000

DEFAULT_DRIVE_NAME = 'Drive'

PASSWORD_STORE_ALL = 0x65766173
PASSWORD_RESTORE_ALL = 0x64616F6C
PASSWORD_STORE_RESTORE_TCP_IP = 0x636F6D73
PASSWORD_STORE_RESTORE_SUB_0 = 0x73756230


def _load():
    """Load IngeniaLink constants to this module."""
    module = sys.modules[__name__]
    const_pattern = re.compile('ILK_(.*)')

    # add all constants to the module dictionary
    for k in lib.__dict__:
        m = const_pattern.match(k)
        if m:
            name = m.groups()[0]
            module.__dict__[name] = lib.__dict__[k]


_load()
