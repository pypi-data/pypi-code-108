"""
Taktile Auth
"""
import pkg_resources

__version__ = pkg_resources.get_distribution(
    __name__.split(".", maxsplit=1)[0]
).version
