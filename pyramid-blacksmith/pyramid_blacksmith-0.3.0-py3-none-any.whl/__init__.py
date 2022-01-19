import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("pyramid-blacksmith").version
except pkg_resources.DistributionNotFound:
    # read the doc does not support poetry
    pass

from .binding import PyramidBlacksmith, includeme
from .middleware import AbstractMiddlewareBuilder
from .middleware_factory import AbstractMiddlewareFactoryBuilder

__all__ = [
    "PyramidBlacksmith",
    "includeme",
    "AbstractMiddlewareBuilder",
    "AbstractMiddlewareFactoryBuilder",
]
