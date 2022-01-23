from .ocs_academic_hub import HubClient
from .util import timer

from importlib_metadata import version

__version__ = version("ocs_academic_hub")


__all__ = ["HubClient", "timer", "__version__"]
