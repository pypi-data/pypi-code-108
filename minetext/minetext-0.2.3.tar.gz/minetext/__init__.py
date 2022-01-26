from .domain.es_request import EsRequest
from .mine import Mine

VERSION = (0, 2, 0)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))

__all__ = [
    'Mine',
    'EsRequest'
]
