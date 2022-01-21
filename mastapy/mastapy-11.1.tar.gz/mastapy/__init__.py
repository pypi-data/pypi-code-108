'''__init__.py

This is the root of the mastapy package.

'''


from ._internal import *
from ._internal import (
    __version__, __api_version__,
    _MASTA_PROPERTIES, _MASTA_SETTERS)


load_mastafile()


from ._math import *
