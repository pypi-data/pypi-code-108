# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# Classes and functions constituting the public API of this package.
# By importing them here, we make them importable from the package
# base namespace, i.e., "from ysgrpctelemetry import T_CLASS",
# rather than from the submodule (ysgrpctelemetry.grpctelemetry.T_CLASS).
# Any classes, functions, etc. in this package that are *not* thus published
# should be considered private APIs subject to change.
from .grpctelemetry import YSGrpcTelemetryServer

# Additional storage paths defined by this package, if any
# from yangsuite.paths import register_path
# register_path(...)

# Must be set for auto-discovery by yangsuite core
default_app_config = 'ysgrpctelemetry.apps.YSGrpcTelemetryConfig'

# Boilerplate for versioneer auto-versioning
from ._version import get_versions          # noqa: E402
__version__ = get_versions()['version']
del get_versions

# Classes and functions loaded when calling "from ysgrpctelemetry import *".
# (Although users generally shouldn't do that!)
# Same list as the public API above, typically.
__all__ = (
    'YSGrpcTelemetryServer',
)
