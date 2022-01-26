#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""The detector attribute and data structure subpackage."""

# flake8: noqa
# Warning: Import order matters
from .environment import Environment
from .detector import Detector
from .ccd import CCD
from .cmos import CMOS
from .mkid import MKID
from .geometry import Geometry
from .ccd_geometry import CCDGeometry
from .cmos_geometry import CMOSGeometry
from .mkid_geometry import MKIDGeometry
from .characteristics import Characteristics
from .ccd_characteristics import CCDCharacteristics
from .cmos_characteristics import CMOSCharacteristics
from .mkid_characteristics import MKIDCharacteristics
from .optics import Optics
from .readout_properties import ReadoutProperties
