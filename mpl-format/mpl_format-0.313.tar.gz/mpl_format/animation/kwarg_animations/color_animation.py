from typing import List, Union, Optional

from numpy import linspace, sin, pi, sign, arcsin

from mpl_format.compound_types import Color
from mpl_format.animation.rate import Rate
from mpl_format.utils.color_utils import set_alpha, cross_fade


class ColorAnimation(object):

    def __init__(self,
                 colors: List[Color],
                 t: Optional[List[float]] = None,
                 rate: Optional[Union[Rate, str]] = None):

        self.colors: List[Color] = colors
        if t is not None:
            self.t: List[float] = t
        else:
            self.t = list(linspace(0, 1, len(colors)))
        self.rate: Rate = (
            Rate.linear() if rate is None else
            rate if isinstance(rate, Rate) else
            Rate(rate)
        )

    @staticmethod
    def fade_in(color: Color) -> 'ColorAnimation':

        return ColorAnimation(
            colors=[set_alpha(color, 0), color],
            t=[0, 1]
        )

    @classmethod
    def sine_wave(cls, color_1: Color, color_2: Color,
                  cycles: float, phase: float = 0.0) -> 'ColorAnimation':
        """
        Return a sine wave oscillating between color_1 and color_2,
        starting at phase * 2π with cycles complete waves.

        :param color_1: Lowest color of the wave.
        :param color_2: Highest color of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = 0.5
        amplitude = 0.5
        rate = Rate(lambda t: (
                middle_val +
                amplitude * sin((2 * pi * t * cycles) - (2 * pi * phase))
        ))
        return ColorAnimation(colors=[color_1, color_2],
                              rate=rate)

    @classmethod
    def square_wave(cls, color_1: Color, color_2: Color,
                    cycles: float, phase: float = 0.0) -> 'ColorAnimation':
        """
        Return a square wave oscillating between min_val and max_val,
        starting at phase * 2π with cycles complete waves.

        :param color_1: Lowest color of the wave.
        :param color_2: Highest color of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = 0.5
        amplitude = 0.5
        rate = Rate(lambda t: (
                middle_val +
                amplitude * sign(
                    sin((2 * pi * t * cycles) - (2 * pi * phase))
                )
        ))
        return ColorAnimation(colors=[color_1, color_2],
                              rate=rate)

    @classmethod
    def triangle_wave(cls, color_1: Color, color_2: Color,
                      cycles: float, phase: float = 0.0) -> 'ColorAnimation':
        """
        Return a triangle wave oscillating between min_val and max_val,
        starting at phase * 2π with cycles complete waves.

        :param color_1: Lowest color of the wave.
        :param color_2: Highest color of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = 0.5
        amplitude = 0.5
        rate = Rate(lambda t: (
                middle_val +
                2 * amplitude * arcsin(
                    sin((2 * pi * t * cycles) - (2 * pi * phase))
                ) / pi
        ))
        return ColorAnimation(colors=[color_1, color_2],
                              rate=rate)

    def at(self, t: float) -> Color:

        for i in range(len(self.t)):
            if self.t[i + 1] >= t:
                dt = self.rate(
                    (t - self.t[i]) /
                    (self.t[i + 1] - self.t[i])
                )
                return cross_fade(
                    from_color=self.colors[i],
                    to_color=self.colors[i + 1],
                    amount=dt
                )
