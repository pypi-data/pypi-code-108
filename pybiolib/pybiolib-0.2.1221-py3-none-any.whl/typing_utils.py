import sys

# import and expose everything from the typing module
from typing import *  # pylint: disable=wildcard-import, unused-wildcard-import

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict, Literal
