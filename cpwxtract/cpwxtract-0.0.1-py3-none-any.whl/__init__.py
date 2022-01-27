#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


from jax.config import config

config.update("jax_enable_x64", True)
# config.update("jax_debug_nans", True)

from .__about__ import __author__, __description__, __version__
from .constants import *
from .helpers import *
from .io import *
from .extract import *
from .cpw import *
