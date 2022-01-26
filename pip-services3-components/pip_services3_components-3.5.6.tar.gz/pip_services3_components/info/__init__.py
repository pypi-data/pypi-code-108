# -*- coding: utf-8 -*-
"""
    pip_services3_components.info.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains a simple object that defines the context of execution. For various
    logging functions we need to know what source we are logging from – what is
    the processes name, what the process is/does.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['ContextInfo', 'DefaultInfoFactory']

from .ContextInfo import ContextInfo
from .DefaultInfoFactory import DefaultInfoFactory
