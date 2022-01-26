from .bdata import bdata
from .life import life
from .bjoined import bjoined
from .bmerged import bmerged
from .version import __version__
from .exceptions import InputError, MinimizationError

import os, sys

# get home directory
if sys.platform == 'win32':
    _homedir = os.environ['HOMEPATH']
else:
    _homedir = os.environ['HOME']

# define variables
__all__ = ['bdata', 'bjoined', 'bmerged', 'life', 'calc']
__author__ = 'Derek Fujimoto'
_mud_data = os.path.join(_homedir, '.bdata')
