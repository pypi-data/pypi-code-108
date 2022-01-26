import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version
else:  # for Python<3.8
    from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version("infima_client")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
