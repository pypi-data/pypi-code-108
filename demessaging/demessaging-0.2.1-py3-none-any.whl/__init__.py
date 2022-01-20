"""Main module to start a backend module from the command-line."""
from demessaging.backend import BackendModule, main  # noqa: F401
from demessaging.config import configure, registry

from ._version import get_versions

__all__ = ["main", "configure", "registry", "BackendModule"]


__version__ = get_versions()["version"]
del get_versions
