"""

    .. uml::

        class areas <<(M,#FF7700)>> {
        .. functions ..
        As()
        As_distributed()
        As_for_ω()
        As_layer()
        As1_for_ω1ρ1()
        As2_for_ω2ρ2()
        }

"""

import numpy as np


def As(dia):
    return np.pi * dia**2 / 4


def As_distributed(dia, s):
    """
    Area reinforcement for 1.0m length

    Args:
        dia (float): Bar diameter
        s (float): Distance between bars

    Returns:
        float:

    """

    return As(dia) * 1.0 / s


def As_layer(n, dia):
    """

    Args:
        n (list or integer):
        dia (np.array or float):

    Returns:
        float:
    """

    if isinstance(n, list):
        return sum(np.array(n) * np.array(dia)**2 * np.pi/4)
    else:
        return n * dia**2 * np.pi/4


def As_for_ω(ω, b, d, fc, fy, N):
    """

    Args:
        ω (float):
        b (float): Section width
        d (float): Section effective depth
        fc (float): Concrete compressive strength
        fy (float): Reinforcement steel yield strength
        N (float): Axial force

    Returns:
        float:

    """
    return ω * b * d * fc / fy + N / fy


def As1_for_ω1ρ1(ω1, ρ1, b, d, fc, fy, N):
    return ω1 * ρ1 * b * d * fc / fy + N / fy


def As2_for_ω2ρ2(ω2, ρ2, b, d, fc, fy):
    return ω2 * ρ2 * b * d * fc / fy
