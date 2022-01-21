"""
Easing functions are smooth, real valued functions defined over the range
[0, 1].  Behavior outside this interval is not specified.  See
http://robertpenner.com/easing/ for more info.  Each of these functions takes a
single float in [0, 1] and returns a float in [0, 1].

=====================   =============   ============    ===================
function type           in function     out function    in-out function
=====================   =============   ============    ===================
linear                  linear          linear          linear
2nd degree polynomial   in_p2           out_p2          in_out_p2
3rd degree polynomial   in_p3           out_p3          in_out_p3
4th degree polynomial   in_p4           out_p4          in_out_p4
5th degree polynomial   in_p5           out_p5          in_out_p5
circular                in_circ         out_circ        in_out_circ
sin                     in_sin          out_sin         in_out_sin
exp                     in_exp          out_exp         in_out_exp
=====================   =============   ============    ===================

"""
import math
from enum import Enum

from typing import Callable

from .primitives import clamp01


class EaseDir(Enum):
    """The direction of an easing function"""

    In = 0  #: ease in
    Out = 1  #: ease out
    InOut = 3  #: ease in-out


class EaseType(Enum):
    """The type of an easing function."""
    P1 = 1  #: linear (polynomial of degree 1)
    P2 = 2  #: quadratic (polynomial of degree 2)
    P3 = 3  #: cubic (polynomial of degree 3)
    P4 = 4  #: quartic (polynomial of degree 4)
    P5 = 5  #: quintic (polynomial of degree 5)
    Circ = 6  #: circular
    Sin = 7  #: sin


FloatToFloat = Callable[[float], float]


def linear(t: float) -> float:
    """
    linear easing function

    :param t: input value in range [0,1]
    """
    return t


def in_p2(t: float) -> float:
    """
    quadratic ease-in function

    :param t: input value in range [0,1]
    """
    return t * t


def out_p2(t: float) -> float:
    """
    quadratic ease-out function

    :param t: input value in range [0,1]
    """
    return 1.0 - (1.0 - t) * (1.0 - t)


def in_out_p2(t: float) -> float:
    """
    quadratic ease-in-out  function

    :param t: input value in range [0,1]
    """
    return in_p2(2.0 * t) / 2.0 if (t < 0.5) else 1.0 - in_p2(
        2.0 * (1.0 - t)) / 2.0


def in_p3(t: float) -> float:
    """
    cubic ease-in function

    :param t: input value in range [0,1]
    """
    return t * t * t


def out_p3(t: float) -> float:
    """
    cubic ease-out function

    :param t: input value in range [0,1]
    """
    return 1.0 - in_p4(1.0 - t)


def in_out_p3(t: float) -> float:
    """
    cubic ease-in-out function

    :param t: input value in range [0,1]
    """
    return in_p3(2.0 * t) / 2.0 if (t < 0.5) else 1.0 - in_p3(
        2 * (1.0 - t)) / 2.0


def in_p4(t: float) -> float:
    """
    quartic ease-in function

    :param t: input value in range [0,1]
    """
    return t * t * t * t


def out_p4(t: float) -> float:
    """
    quartic ease-out function

    :param t: input value in range [0,1]
    """
    return 1.0 - in_p4(1.0 - t)


def in_out_p4(t: float) -> float:
    """
    quartic ease-in-out function

    :param t: input value in range [0,1]
    """
    return in_p4(2.0 * t) / 2.0 if (t < 0.5) else 1.0 - in_p4(
        2.0 * (1.0 - t)) / 2.0


def in_p5(t: float) -> float:
    """
    quintic ease-in function

    :param t: input value in range [0,1]
    """
    return t * t * t * t * t


def out_p5(t: float) -> float:
    """
    quintic ease-out function

    :param t: input value in range [0,1]
    """
    return 1 - in_p5(1.0 - t)


def in_out_p5(t: float) -> float:
    """
    quintic ease-in-out function

    :param t: input value in range [0,1]
    """
    return in_p5(2.0 * t) / 2.0 if (t < 0.5) else 1.0 - in_p5(
        2.0 * (1.0 - t)) / 2.0


def in_circ(t: float) -> float:
    """
    circular ease-in function

    :param t: input value in range [0,1]
    """
    return 1.0 - math.sqrt(1.0 - t * t)


def out_circ(t: float) -> float:
    """
    circular ease-out function

    :param t: input value in range [0,1]
    """
    return 1.0 - in_circ(1.0 - t)


def in_out_circ(t: float) -> float:
    """
    circular ease-in-out function

    :param t: input value in range [0,1]
    """
    return in_circ(2.0 * t) / 2.0 if (t < 0.5) else 1.0 - in_circ(
        2.0 * (1.0 - t)) / 2.0


def in_sin(t: float) -> float:
    """
    sin ease-in function

    :param t: input value in range [0,1]
    """
    return 1.0 - math.cos(t * math.pi / 2.0)


def out_sin(t: float) -> float:
    """
    sin ease-out function

    :param t: input value in range [0,1]
    """
    return math.sin(t * math.pi / 2.0)


def in_out_sin(t: float) -> float:
    """
    sin ease-in-out function

    :param t: input value in range [0,1]
    """
    return 0.5 * (1.0 - math.cos(t * math.pi))


def make_in_exp(alpha: float, clamp: bool = False) -> FloatToFloat:
    """
    Make an exp ease-in function with scale alpha.  alpha==0 yields a linear
    function.

    :param alpha: The exponent scale
    :param clamp: wheter we should clamp the  input range to [0,1]

    """
    if alpha == 0.0:
        f = lambda t: t
    else:
        k = 1.0 / (math.exp(alpha) - 1.0)
        f = lambda t: (math.exp(alpha * t) - 1.0) * k
    if clamp:
        return lambda t: f(clamp01(t))
    else:
        return f


def make_out_exp(alpha: float, clamp: bool = False) -> FloatToFloat:
    """
    Make an exp ease-in function with scale alpha.  alpha==0 yields a linear
    function.

    :param alpha: The exponent scale
    :param clamp: wheter we should clamp the  input range to [0,1]

    """
    if alpha == 0.0:
        f = lambda t: t
    else:
        k = 1.0 / (math.exp(alpha) - 1.0)
        f = lambda t: 1.0 - (math.exp(alpha * (1.0 - t)) - 1.0) * k
    if clamp:
        return lambda t: f(clamp01(t))
    else:
        return f


def make_in_out_exp(alpha: float, clamp: bool = True) -> FloatToFloat:
    """
    Make an exp ease-in-out function with scale alpha.  alpha==0 yields a linear
    function.

    :param alpha: The exponent scale
    :param clamp: wheter we should clamp the  input range to [0,1]

    """
    if alpha == 0.0:
        if clamp:
            return lambda t: clamp01(t)
        else:
            return lambda t: t
    f = make_in_exp(alpha)

    if clamp:
        def _(t: float) -> float:
            if t < 0.5:
                return f(2.0 * t) * 0.5
            else:
                return 1.0 - f(2.0 * (1.0 - t)) * 0.5
    else:
        def _(t: float) -> float:
            if t <= 0:
                return 0.0
            elif t < 0.5:
                return f(2.0 * t) * 0.5
            elif t < 1.0:
                return 1.0 - f(2.0 * (1.0 - t)) * 0.5
            else:
                return 1.0
    return _


__EASE_FUNCS = {
    (EaseType.P1, EaseDir.In):      linear,
    (EaseType.P1, EaseDir.Out):     linear,
    (EaseType.P1, EaseDir.InOut):   linear,
    (EaseType.P2, EaseDir.In):      in_p2,
    (EaseType.P2, EaseDir.Out):     out_p2,
    (EaseType.P2, EaseDir.InOut):   in_out_p2,
    (EaseType.P3, EaseDir.In):      in_p3,
    (EaseType.P3, EaseDir.Out):     out_p3,
    (EaseType.P3, EaseDir.InOut):   in_out_p3,
    (EaseType.P4, EaseDir.In):      in_p4,
    (EaseType.P4, EaseDir.Out):     out_p4,
    (EaseType.P4, EaseDir.InOut):   in_out_p4,
    (EaseType.P5, EaseDir.In):      in_p5,
    (EaseType.P5, EaseDir.Out):     out_p5,
    (EaseType.P5, EaseDir.InOut):   in_out_p5,
    (EaseType.Circ, EaseDir.In):    in_circ,
    (EaseType.Circ, EaseDir.Out):   out_circ,
    (EaseType.Circ, EaseDir.InOut): in_out_circ,
    (EaseType.Sin, EaseDir.In):     in_sin,
    (EaseType.Sin, EaseDir.Out):    out_sin,
    (EaseType.Sin, EaseDir.InOut):  in_out_sin,

}


def make_ease_func(ease_type: EaseType, ease_dir: EaseDir,
                   clamp: bool = True) -> Callable[[float], float]:
    """
    Create an easing function of the given type with the given direction

    :param ease_type: The type of easing function to create
    :param ease_dir: The direction of the easing function
    :param clamp: Clamp the input range to [0,1] if True
    :return: the requested easing function

    """

    f = __EASE_FUNCS[(ease_type, ease_dir)]
    if clamp:
        return lambda t: f(clamp01(t))
    else:
        return f
