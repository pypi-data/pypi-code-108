from .compare_keywords import compare_keywords
from .version import VERSION
__version__ = VERSION

class HTTPCompare(compare_keywords):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
