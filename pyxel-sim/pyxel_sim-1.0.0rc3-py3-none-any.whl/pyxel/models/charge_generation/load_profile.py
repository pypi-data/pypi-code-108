#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to load charge profiles."""

import logging
import typing as t
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from pyxel.data_structure import Charge
from pyxel.detectors import Detector, Geometry
from pyxel.detectors.geometry import (
    get_horizontal_pixel_center_pos,
    get_vertical_pixel_center_pos,
)

# TODO: more documentation, private function


@lru_cache(maxsize=128)  # One must add parameter 'maxsize' for Python 3.7
def _create_charges(
    num_rows: int,
    num_cols: int,
    pixel_vertical_size: float,
    pixel_horizontal_size: float,
    txt_file: str,
    profile_position_y: int,
    profile_position_x: int,
    fit_profile_to_det: bool = False,
) -> pd.DataFrame:
    """Create charges from a charge profile file."""
    # All pixels has zero charge by default
    detector_charge_2d = np.zeros((num_rows, num_cols))

    # Load 2d charge profile (which can be smaller or
    #                         larger in dimensions than detector imaging area)
    full_path = Path(txt_file).resolve()
    charges_from_file_2d = np.loadtxt(str(full_path), ndmin=2)  # type: np.ndarray
    # TODO: use pyxel function load_table?

    if fit_profile_to_det:
        # Crop 2d charge profile, so it is not larger in dimensions than detector imaging area)
        charges_from_file_2d = charges_from_file_2d[
            slice(0, num_rows), slice(0, num_cols)
        ]

    profile_rows, profile_cols = charges_from_file_2d.shape

    detector_charge_2d[
        slice(profile_position_y, profile_position_y + profile_rows),
        slice(profile_position_x, profile_position_x + profile_cols),
    ] = charges_from_file_2d

    charge_numbers = detector_charge_2d.flatten()  # type: np.ndarray
    where_non_zero = np.where(charge_numbers > 0.0)
    charge_numbers = charge_numbers[where_non_zero]
    size = charge_numbers.size  # type: int

    vertical_pixel_center_pos_1d = get_vertical_pixel_center_pos(
        num_rows=num_rows,
        num_cols=num_cols,
        pixel_vertical_size=pixel_vertical_size,
    )

    horizontal_pixel_center_pos_1d = get_horizontal_pixel_center_pos(
        num_rows=num_rows,
        num_cols=num_cols,
        pixel_horizontal_size=pixel_horizontal_size,
    )

    init_ver_pix_position_1d = vertical_pixel_center_pos_1d[where_non_zero]
    init_hor_pix_position_1d = horizontal_pixel_center_pos_1d[where_non_zero]

    # Create new charges
    return Charge.create_charges(
        particle_type="e",
        particles_per_cluster=charge_numbers,
        init_energy=np.zeros(size),
        init_ver_position=init_ver_pix_position_1d,
        init_hor_position=init_hor_pix_position_1d,
        init_z_position=np.zeros(size),
        init_ver_velocity=np.zeros(size),
        init_hor_velocity=np.zeros(size),
        init_z_velocity=np.zeros(size),
    )


# TODO: Fix this
# @validators.validate
# @config.argument(name='txt_file', label='file path', units='', validate=checkers.check_path)
def charge_profile(
    detector: Detector,
    txt_file: t.Union[str, Path],
    fit_profile_to_det: bool = False,
    profile_position: t.Optional[t.Tuple[int, int]] = None,
) -> None:
    """Load charge profile from txt file for detector, mostly for but not limited to CCDs.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    txt_file : str or Path
        File path.
    fit_profile_to_det : bool
    profile_position : list
    """
    logging.info("")

    if profile_position is None:
        profile_position_y = 0  # type: int
        profile_position_x = 0  # type: int
    else:
        profile_position_y, profile_position_x = profile_position

    geo = detector.geometry  # type: Geometry

    # Create charges as `DataFrame`
    charges = _create_charges(
        num_rows=geo.row,
        num_cols=geo.col,
        pixel_vertical_size=geo.pixel_vert_size,
        pixel_horizontal_size=geo.pixel_horz_size,
        txt_file=txt_file,
        profile_position_y=profile_position_y,
        profile_position_x=profile_position_x,
        fit_profile_to_det=fit_profile_to_det,
    )  # type: pd.DataFrame

    # Add charges in 'detector'
    detector.charge.add_charge_dataframe(charges)
