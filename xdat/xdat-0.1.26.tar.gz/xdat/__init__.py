"""

"""

__version__ = "0.1.0"
__author__ = 'Ido Carmi'
__credits__ = 'Hermetric Software Services Ltd.'


# import pandas_sets
from . import xagg, xcache, xchecks, xmunge, xnp, xpd, xplt


def monkey_patch():
    xpd.monkey_patch()
    xnp.monkey_patch()

