#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to convert photon into photo-electrons inside detector."""
import typing as t
from pathlib import Path

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image


def apply_qe(array: np.ndarray, qe: t.Union[float, np.ndarray]) -> np.ndarray:
    """Apply quantum efficiency to an array.

    Parameters
    ----------
    array: np.ndarray
    qe: ndarray or float
        Quantum efficiency.

    Returns
    -------
    ndarray
    """
    return array * qe


def simple_conversion(
    detector: Detector, quantum_efficiency: t.Optional[float] = None
) -> None:
    """Generate charge from incident photon via photoelectric effect, simple model.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    quantum_efficiency: float, optional
        Quantum efficiency.
    """
    if quantum_efficiency is None:
        final_qe = detector.characteristics.quantum_efficiency
    else:
        final_qe = quantum_efficiency

    if not 0 <= final_qe <= 1:
        raise ValueError("Quantum efficiency not between 0 and 1.")

    detector_charge = apply_qe(array=detector.photon.array, qe=final_qe)
    detector.charge.add_charge_array(detector_charge)


def conversion_with_qe_map(
    detector: Detector,
    filename: t.Union[str, Path],
    position: t.Tuple[int, int] = (0, 0),
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
) -> None:
    """Generate charge from incident photon via photoelectric effect, simple model with custom :term:`QE` map.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        File path.
    position: tuple
        Indices of starting row and column, used when fitting :term:`QE` map to detector.
    align: Literal
        Keyword to align the :term:`QE` map to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    """
    geo = detector.geometry
    position_y, position_x = position

    # Load charge profile as numpy array.
    qe = load_cropped_and_aligned_image(
        shape=(geo.row, geo.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )  # type: np.ndarray

    if not np.all((0 <= qe) & (qe <= 1)):
        raise ValueError("Quantum efficiency values not between 0 and 1.")

    detector_charge = apply_qe(array=detector.photon.array, qe=qe)
    detector.charge.add_charge_array(detector_charge)


# # TODO: Fix this
# # @validators.validate
# # @config.argument(name='', label='', units='', validate=)
# def monte_carlo_conversion(detector: Detector) -> None:
#     """Generate charge from incident photon via photoelectric effect, more exact, stochastic (Monte Carlo) model.
#
#     :param detector: Pyxel Detector object
#     """
#     logging.info("")
#
#     # detector.qe <= 1
#     # detector.eta <= 1
#     # if np.random.rand(size) <= detector.qe:
#     #     pass    # 1 e
#     # else:
#     #     pass
#     # if np.random.rand(size) <= detector.eta:
#     #     pass    # 1 e
#     # else:
#     #     pass
#     # TODO: random number for QE
#     # TODO: random number for eta
#     # TODO: energy threshold
#
#
# def random_pos(detector: Detector) -> None:
#     """Generate random position for photoelectric effect inside detector.
#
#     :param detector: Pyxel Detector object
#     """
#     # pos1 = detector.vert_dimension * np.random.random()
#     # pos2 = detector.horz_dimension * np.random.random()
#
#     # size = 0
#     # pos3 = -1 * detector.total_thickness * np.random.rand(size)
#     # return pos3
#     raise NotImplementedError
