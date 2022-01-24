from .mql import MQLClient

__version__ = "0.0.60"
PACKAGE_NAME = "transform"

# mql gets imported if user is already authenticated
mql = None
try:
    mql = MQLClient()
except Exception as e:  # noqa: D
    pass
