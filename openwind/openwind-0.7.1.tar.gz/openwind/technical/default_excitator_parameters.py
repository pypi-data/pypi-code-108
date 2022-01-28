#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

"""
This module contains dictionnaries that are used by the
:py:class:`Player <openwind.technical.player.Player>` class

Available dictionnaries are :

- 'WOODWIND_REED': a default Reed1dof excitator with woodwind-reed convention (inward)
- 'LIPS': a default Reed1dof excitator with lips convention (outward)
- 'UNITARY_FLOW': a Flow excitator, with flow imposed to 1
- 'TUTORIAL_LIPS': lips with parameters adapted for tutorial geometry
- 'TUTORIAL_REED': woodwind-reed with parameters adapted for tutorial geometry
- 'OBOE': reed with parameters corresponding to oboe reed
- 'CLARINET': reed with parameters corresponding to clarinet reed
- 'ZERO_FLOW': a Flow excitator, with flow imposed to 0
- 'IMPULSE_100us': a Flow excitator corresponding to an impulse with \
    characteristic time set to 100 micro-sec.
- 'IMPULSE_400us': a Flow excitator corresponding to an impulse with \
    characteristic time set to 400 micro-sec.
"""

import numpy as np
from openwind.technical.temporal_curves import constant_with_initial_ramp, dirac_flow, triangle


WOODWIND_REED = {
    "excitator_type" : "Reed1dof",
    "opening" : 1e-4,
    "mass" : 3.376e-6,
    "section" : 14.6e-5,
    "pulsation" : 2*np.pi*3700,
    "dissip" : 3000,
    "width" : 3e-2,
    "mouth_pressure" : constant_with_initial_ramp(2000, 2e-2),
    "model" : "inwards",
        #  valeurs de Bilbao 2008
    "contact_pulsation": 316,
    "contact_exponent": 4
}

# from Fréour et al, JASA 2020
LIPS = {
    "excitator_type" : "Reed1dof",
    "opening" : 1e-4,
    "mass" : 8e-5,
    "section" : 4e-5,
    "pulsation" : 2*np.pi*382,
    "dissip" : 0.3*2*np.pi*382,
    "width" : 8e-3,
    "mouth_pressure" : constant_with_initial_ramp(5500, 1e-2),#triangle(3200, .5),
    "model" : "outwards",
    "contact_pulsation": 0*316,
    "contact_exponent": 4
}

# These parameters are only used by the basic tutorial
# but they do not correspond to anything physical
TUTORIAL_LIPS = {
    "excitator_type" : "Reed1dof",
    "opening" : 9.4e-4,
    "mass" : 6.4e-5,
    "section" : 1.9e-4,
    "pulsation" : 2*np.pi*750,
    "dissip" : 0.7*2*np.pi*750,
    "width" : 11.9e-3,
    "mouth_pressure" : constant_with_initial_ramp(5000, 1e-2),
    "model" : "outwards",
    "contact_pulsation": 0,
    "contact_exponent": 4
}

TUTORIAL_REED = {
    "excitator_type" : "Reed1dof",
    "opening" : 9.4e-4,
    "mass" : 6.4e-5,
    "section" : 1.9e-4,
    "pulsation" : 2*np.pi*750,
    "dissip" : 0.7*2*np.pi*750,
    "width" : 11.9e-3,
    "mouth_pressure" : constant_with_initial_ramp(5000, 1e-2),
    "model" : "inwards",
    "contact_pulsation": 0,
    "contact_exponent": 4
}

OBOE = {
    "excitator_type" : "Reed1dof",
    "opening" : 8.9e-5,
    "mass" : 7.1e-4,
    "section" : 4.5e-5,
    "pulsation" : 2*np.pi*600,
    "dissip" : 0.4*2*np.pi*600,
    "width" : 9e-3,
    "mouth_pressure" : constant_with_initial_ramp(12000, 2e-2),
    "model" : "inwards",
    "contact_pulsation": 316,
    "contact_exponent": 4
}

# values of Bilbao 2008
CLARINET = {
    "excitator_type" : "Reed1dof",
    "opening" : 4e-4,
    "mass" : 3.376e-6,
    "section" : 14.6e-5,
    "pulsation" : 2*np.pi*3700,
    "dissip" : 3000,
    "width" : 3e-2,
    "mouth_pressure" : constant_with_initial_ramp(2000, 2e-2),
    "model" : "inwards",
    "contact_pulsation": 316,
    "contact_exponent": 4
}


UNITARY_FLOW = {
    "excitator_type":"Flow",
    "input_flow":1
}

ZERO_FLOW = {
    "excitator_type":"Flow",
    "input_flow":0
}

IMPULSE_400us = {
    "excitator_type":"Flow",
    "input_flow": dirac_flow(4e-4)
}

IMPULSE_100us = {
    "excitator_type":"Flow",
    "input_flow": dirac_flow(1e-4)
}
