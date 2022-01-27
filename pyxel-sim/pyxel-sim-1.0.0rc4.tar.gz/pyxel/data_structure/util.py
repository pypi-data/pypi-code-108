#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel util functions for Particle classes."""

import math
import typing as t

import numpy as np


def check_energy(initial_energy: t.Union[int, float]) -> None:
    """Check energy of the particle if it is a float or int.

    :param initial_energy:
    :return:
    """
    if not isinstance(initial_energy, (int, float)):
        raise TypeError("Given particle energy could not be read")


def random_direction(
    v_abs: float = 1.0, seed: t.Optional[int] = None
) -> np.ndarray:  # TODO check random angles and direction
    """Generate random direction for a photon.

    Parameters
    ----------
    v_abs: float
    seed: int
    """
    rng = np.random.default_rng(seed=seed)
    alpha = 2 * math.pi * rng.random()
    beta = 2.0 * math.pi * rng.random()
    v_z = v_abs * math.sin(alpha)
    v_ver = v_abs * math.cos(alpha) * math.cos(beta)
    v_hor = v_abs * math.cos(alpha) * math.sin(beta)
    return np.array([v_ver, v_hor, v_z])
