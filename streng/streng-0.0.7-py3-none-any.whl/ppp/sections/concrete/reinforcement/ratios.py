"""

    .. uml::

        class ratios <<(M,#FF7700)>> {
        .. functions ..
        ρ()
        ρw()
        ω()
        }

"""

import math
from . import areas


def ρ(As, b, d):
    """
        Ποσοστό διαμήκους οπλισμού

    Args:
        As (float): Reinforcement area
        b (float): Section width
        d (float): Section effective depth

    Returns:
        float:
    """
    return As / (b * d)


def ρw(nw, diaw, b, s, α=math.pi/2):
    """
        Ποσοστό εγκάρσιου οπλισμού

    Args:
        nw (float): Τμήσεις συνδετήρα
        diaw (float): Διάμετρος συνδετήρα
        b (float): Section width
        s (float): Space between transverse reinforcement
        α (float): Transverse reinforcement angle

    Returns:
        float:
    """
    Asw = nw * areas.As(diaw)
    return Asw / (b * s * math.sin(α))


def ρw_vol(hoops_length, diaw, b, h, s):
    """
        Ογκομετρικό ποσοστό εγκάρσιου οπλισμού

    Args:
        hoops_length (float): Συνολικό μήκος σκελών συνδετήρων
        diaw (float): Διάμετρος συνδετήρα
        b (float): Section width
        h (float): Section height
        s (float): Space between transverse reinforcement

    Returns:
        float:
    """
    return hoops_length * areas.As(diaw) / (b * h * s)



def ω(As: float, b: float, d: float, fy: float, fc: float):
    """
        Μηχανικά ποσοστά οπλισμού

    Args:
        As (float): Reinforcement area
        b (float): Section width
        d (float): Section effective depth
        fy (float):
        fc (float):

    Returns:
        float:
    """
    return As / (b * d) * (fy / fc)
