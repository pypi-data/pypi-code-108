# -*- coding: utf-8 -*-
"""
    pip_services3_components.build.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains the "factory design pattern". There are various factory types,
    which are also implemented in a portable manner.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['IFactory', 'CreateException', 'CompositeFactory', 'Factory']

from .CompositeFactory import CompositeFactory
from .CreateException import CreateException
from .Factory import Factory
from .IFactory import IFactory
