#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 00:35:22 2022

@author: Mohammad Asim
"""

import logging
from .input import Input

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
__all__ = [
    'Input'
]