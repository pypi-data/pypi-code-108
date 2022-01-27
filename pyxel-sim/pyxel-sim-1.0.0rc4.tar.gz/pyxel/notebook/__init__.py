#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
"""Notebook functions."""

# flake8: noqa
from .jupyxel import (
    display_config,
    display_dict,
    display_model,
    change_modelparam,
    display_array,
    display_detector,
    display_persist,
)
from .html_representation import display_html

from .calibration import (
    display_calibration_inputs,
    display_simulated,
    display_evolution,
    champion_heatmap,
    optimal_parameters,
)

import holoviews as hv  # TODO: Remove this will speed-up the import time. See #321

hv.extension("bokeh")  # TODO: Remove this will speed-up the import time. See #321
