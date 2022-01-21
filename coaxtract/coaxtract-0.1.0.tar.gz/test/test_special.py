#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


import jax.numpy as jnp
import numpy as np
from jax.config import config

from coaxtract.special import *

config.update("jax_enable_x64", True)


def test_j0():
    z = jnp.linspace(0, 20, 10000)

    assert jnp.allclose(j0(z), j0_scipy(z), atol=5e-6)
