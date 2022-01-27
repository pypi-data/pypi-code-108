#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Stripe pattern illumination model."""

import typing as t

import numpy as np
import skimage.transform as tr

if t.TYPE_CHECKING:
    from pyxel.detectors import Detector


def square_signal(n: int, lw: int, start_with: int = 0) -> t.List[int]:
    """Compute a 1D periodic square signal.

    Parameters
    ----------
    n: int
        Length of the signal.
    lw:
        Width of a pulse.
    start_with
        1 to start with high level or 0 for 0.

    Returns
    -------
    out: list
        Output list.
    """
    if lw > n // 2:
        raise ValueError("Line too wide.")
    start = [start_with] * lw  # type: t.List[int]
    second = [1 - start_with] * lw  # type: t.List[int]
    pair = start + second
    num = n // len(pair)
    out = pair * num
    return out


def compute_pattern(
    detector_shape: tuple,
    period: int = 2,
    level: float = 1,
    angle: float = 0,
    start_with: int = 0,
) -> np.ndarray:
    """Return an array of a periodic pattern.

    Parameters
    ----------
    detector_shape: tuple
        Detector shape.
    period: int
        Period of the periodic pattern in pixels.
    level: float
        Amplitude of the periodic pattern.
    angle: int
        Angle of the pattern in degrees.
    start_with: int
        1 to start with high level or 0 for 0.

    Returns
    -------
    out: ndarray
        Output stripe pattern.
    """

    if period < 2:
        raise ValueError("Can not set a period smaller than 2 pixels.")
    elif (period % 2) != 0:
        raise ValueError("Period should be a multiple of 2.")
    if start_with not in [0, 1]:
        raise ValueError("")

    y, x = detector_shape

    n = max(y, x) * 2
    m = max(y, x) * 2

    sx = slice(n // 2 - y // 2, n // 2 + y // 2)
    sy = slice(m // 2 - x // 2, m // 2 + x // 2)

    signal_lst = square_signal(
        n=n, lw=period // 2, start_with=start_with
    )  # type: t.List[int]
    new_signal_lst = signal_lst + ([1] * (n - len(signal_lst)))  # type: t.List[int]
    signal = np.array(new_signal_lst)[::-1]

    out = np.ones((n, m))

    for i in range(m):
        out[:, i] = signal

    out = level * out

    if angle:
        out = tr.rotate(out, angle=angle)

    out = out[sx, sy]

    return out


def stripe_pattern(
    detector: "Detector",
    period: int = 10,
    level: float = 1.0,
    angle: int = 0,
    startwith: int = 0,
    time_scale: float = 1.0,
) -> None:
    """Stripe pattern model.

    Parameters
    ----------
    detector: Detector
        Detector object.
    period: int
        Period of the periodic pattern in pixels.
    level: float
        Amplitude of the periodic pattern.
    angle: int
        Angle of the pattern in degrees.
    startwith: int
        1 to start with high level or 0 for 0.
    time_scale: float
        Time scale of the photon flux, default is 1 second. 0.001 would be ms.
    """

    photon_array = compute_pattern(
        detector_shape=(detector.geometry.row, detector.geometry.col),
        period=period,
        level=level,
        start_with=startwith,
        angle=angle,
    )

    photon_array = photon_array * (detector.time_step / time_scale)

    try:
        detector.photon.array += photon_array
    except ValueError as ex:
        raise ValueError("Shapes of arrays do not match") from ex
