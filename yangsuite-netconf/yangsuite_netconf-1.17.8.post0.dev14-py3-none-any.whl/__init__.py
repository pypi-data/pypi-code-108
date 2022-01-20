# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# Classes and functions constituting the public API of this package
# These can be imported from the package base namespace,
# i.e. "from ysnetconf import YSNetconfRPCBuilder".
# Objects not in this list should be considered private APIs and
# should not be called directly by other packages if at all possible.
from .nconf import (
    ncclient_send,
    ncclient_supported_platforms,
)
from .rpcbuilder import YSNetconfRPCBuilder

# Must be set for auto-discovery by yangsuite core
default_app_config = 'ysnetconf.apps.YSNetconfConfig'

# Boilerplate for versioneer auto-versioning
from ._version import get_versions         # noqa: E402
__version__ = get_versions()['version']
del get_versions

# Classes and functions obtained as a result of "from ysnetconf import *"
# (although you shouldn't generally do that!)
# Same list as the public API above in most cases.
__all__ = (
    'YSNetconfRPCBuilder',
    'ncclient_send',
    'ncclient_supported_platforms',
)
