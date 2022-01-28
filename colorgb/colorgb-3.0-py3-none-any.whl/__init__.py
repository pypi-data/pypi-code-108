__title__ = "colorgb"
__version__ = "3.0"
__authors__ = "LyQuid"
__license__ = "MIT License"
__copyright__ = "Copyright 2022-present LyQuid"

try:
    from colorama import init
except ImportError:
    raise TypeError("You need install colorama modules. Install : pip install colorama")

init()

from .foregrounds import fore
from .backgrounds import bg
from .styles import style
from .special import blink
