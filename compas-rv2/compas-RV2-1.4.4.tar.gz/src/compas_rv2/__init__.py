"""
********************************************************************************
compas_rv2
********************************************************************************

.. currentmodule:: compas_rv2


.. toctree::
    :maxdepth: 1

    compas_rv2.datastructures
    compas_rv2.rhino
    compas_rv2.scene

"""

from __future__ import print_function

import os


__author__ = ['tom van mele <van.mele@arch.ethz.ch>']
__copyright__ = 'Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'van.mele@arch.ethz.ch'
__version__ = '1.4.4'


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))

__all_plugins__ = ['compas_rv2.install']
# __all__ = ['HOME', 'DATA', 'DOCS', 'TEMP']
