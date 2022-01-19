from typing import Iterable, Union, List

from matplotlib.colors import to_rgb, to_rgba

from compound_types.built_ins import FloatOrFloatIterable
from mpl_format.compound_types import Color


def cross_fade(
        from_color: Color, to_color: Color,
        amount: FloatOrFloatIterable,
) -> Union[Color, List[Color]]:
    """
    Return a new color which fades amount proportion of the way between the 2
    colors.

    :param from_color: The color to fade from.
    :param to_color: The color to fade to.
    :param amount: The amount to fade by, from 0.0 to 1.0
    """
    if isinstance(amount, Iterable):
        return [
            cross_fade(from_color, to_color, amt)
            for amt in amount
        ]
    if isinstance(from_color, str):
        from_color = to_rgb(from_color)
    if isinstance(to_color, str):
        to_color = to_rgb(to_color)

    return tuple([from_value + amount * (to_value - from_value)
                  for from_value, to_value in zip(from_color, to_color)])


def blacken(
        color: Color, amount: FloatOrFloatIterable
) -> Union[Color, List[Color]]:
    """
    Return a color or colors amount fraction or fractions of the way from
    `color` to `black`.

    :param color: The existing color.
    :param amount: The proportion to blacken by.
    """
    return cross_fade(from_color=color, to_color='black',
                      amount=amount)


def whiten(
        color: Color, amount: FloatOrFloatIterable
) -> Union[Color, List[Color]]:
    """
    Return a color or colors amount fraction or fractions of the way from
    `color` to `white`.

    :param color: The existing color.
    :param amount: The proportion to blacken by.
    """
    return cross_fade(from_color=color, to_color='white',
                      amount=amount)


def set_alpha(color: Color, alpha: float) -> Color:
    """
    Set the alpha level of a color to a given value.

    :param color: The existing color.
    :param alpha: The new alpha level
    """
    color = to_rgba(color)
    color = (color[0], color[1], color[2], alpha)
    return color
