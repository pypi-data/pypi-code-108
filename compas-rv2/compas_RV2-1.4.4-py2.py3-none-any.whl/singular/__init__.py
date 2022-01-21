"""
********************************************************************************
compas_rv2.singular
********************************************************************************

.. currentmodule:: compas_rv2.singular


.. toctree::
    :maxdepth: 1

    compas_rv2.singular.algorithms
    compas_rv2.singular.datastructures
    compas_rv2.singular.rhino
    compas_rv2.singular.geometry
    compas_rv2.singular.topology
    compas_rv2.singular.utilities

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os


__author__ = ['Robin Oval', ]
__copyright__ = 'Copyright 2019 - Block Research Group, ETH Zurich'
__license__ = 'MIT License'
__email__ = 'rpho2@cam.ac.uk'

__version__ = '0.1.5'


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, '../..'))
DATA = os.path.abspath(os.path.join(HERE, '../../data'))
TEMP = os.path.abspath(os.path.join(HERE, '../../temp'))

__all__ = []
