"""
:mod:`moke`
===========

Moke is not like ``make``. See the documentation.

"""
from .core import *
from .util import *
# this is for chained pipes of moke scripts
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
del signal
