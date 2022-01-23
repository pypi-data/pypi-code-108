from os import *

if name == 'nt':
    # shadowing os with local definitions
    from .path import *
    from . import path

    sep = '/'
