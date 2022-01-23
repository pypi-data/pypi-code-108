import pkg_resources
__version__ = pkg_resources.get_distribution("sosi_api").version

from .client import BaseClient
