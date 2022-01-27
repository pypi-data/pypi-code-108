#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of cpwxtract
# License: GPLv3
# See the documentation at benvial.gitlab.io/cpwxtract


from jax.config import config

config.update("jax_enable_x64", True)
# config.update("jax_debug_nans", True)

from .__about__ import __author__, __description__, __version__
from .constants import *
from .cpw import *
from .extract import *
from .helpers import *
from .io import *
