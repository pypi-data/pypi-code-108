#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Functions for assigning custom QE maps."""

import typing as t
from pathlib import Path

from pyxel import load_image

if t.TYPE_CHECKING:
    from pyxel.detectors import Detector

# TODO: not a real model, just changing characteristics, move code to the conversion model


def qe_map(
    detector: "Detector",
    filename: t.Union[str, Path],
    fit_qe_to_det: bool = False,
    position_x: int = 0,
    position_y: int = 0,
) -> None:
    """Upload from file and assign a custom QE map to a detector.

    Parameters
    ----------
    detector: Detector
    filename: str or Path
    fit_qe_to_det: bool
    position_x: int
    position_y: int

    Returns
    -------
    None
    """
    qe = load_image(filename)

    rows = detector.geometry.row
    columns = detector.geometry.col

    if rows + position_y > qe.shape[0]:
        raise ValueError("Shapes do not match in Y direction.")
    if columns + position_x > qe.shape[1]:
        raise ValueError("Shapes do not match in X direction.")

    if fit_qe_to_det:
        qe = qe[
            slice(position_y, position_y + rows),
            slice(position_x, position_x + columns),
        ]

    detector.characteristics.quantum_efficiency = qe
