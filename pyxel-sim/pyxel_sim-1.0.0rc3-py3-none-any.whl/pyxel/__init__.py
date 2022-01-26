#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel detector simulation framework."""

# flake8: noqa
from ._version import get_versions

__version__ = get_versions()["version"]  # type: str
del get_versions

from .options import SetOptions as set_options
from .show_versions import show_versions
from .inputs import load_image, load_table, load_datacube
from .configuration import load, save, Configuration
from .run import calibration_mode, exposure_mode, observation_mode, run
from .notebook import (
    display_detector,
    display_persist,
    display_html,
    display_calibration_inputs,
    display_simulated,
    display_evolution,
    champion_heatmap,
    optimal_parameters,
)
