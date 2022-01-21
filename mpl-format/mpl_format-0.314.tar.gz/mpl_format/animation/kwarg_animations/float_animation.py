from numpy import pi, sin, sign, arcsin
from typing import List, Union, Optional

from mpl_format.animation.rate import Rate


class FloatAnimation(object):

    def __init__(self,
                 values: Optional[List[float]] = None,
                 t: Optional[List[float]] = None,
                 rate: Optional[Union[Rate, str]] = None):

        if values is not None:
            self.values: List[float] = values
        else:
            self.values = [0, 1]
        if t is not None:
            self.t: List[float] = t
        else:
            self.t = [0, 1]
        self.rate: Rate = (
            Rate.linear() if rate is None else
            rate if isinstance(rate, Rate) else
            Rate(rate)
        )

    def set_values(self, values: List[float]) -> 'FloatAnimation':

        self.values = values
        return self

    def reverse_values(self) -> 'FloatAnimation':

        return FloatAnimation(
            values=self.values[:: -1],
            t=self.t, rate=self.rate
        )

    @classmethod
    def linear(cls) -> 'FloatAnimation':
        return FloatAnimation(rate='linear')

    @classmethod
    def quadratic(cls) -> 'FloatAnimation':
        return FloatAnimation(rate='quadratic')

    @classmethod
    def cubic(cls) -> 'FloatAnimation':
        return FloatAnimation(rate='cubic')

    @classmethod
    def sine_wave(cls, min_val: float, max_val: float,
                  cycles: float, phase: float = 0.0) -> 'FloatAnimation':
        """
        Return a sine wave oscillating between min_val and max_val,
        starting at phase * 2π with cycles complete waves.

        :param min_val: Lowest value of the wave.
        :param max_val: Highest value of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = (min_val + max_val) / 2
        amplitude = (max_val - min_val) / 2
        rate = Rate(lambda t: (
                middle_val +
                amplitude * sin((2 * pi * t * cycles) - (2 * pi * phase))
        ))
        return FloatAnimation(rate=rate)

    @classmethod
    def square_wave(cls, min_val: float, max_val: float,
                    cycles: float, phase: float = 0.0) -> 'FloatAnimation':
        """
        Return a square wave oscillating between min_val and max_val,
        starting at phase * 2π with cycles complete waves.

        :param min_val: Lowest value of the wave.
        :param max_val: Highest value of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = (min_val + max_val) / 2
        amplitude = (max_val - min_val) / 2
        rate = Rate(lambda t: (
                middle_val +
                amplitude * sign(
                    sin((2 * pi * t * cycles) - (2 * pi * phase))
                )
        ))
        return FloatAnimation(rate=rate)

    @classmethod
    def triangle_wave(cls, min_val: float, max_val: float,
                      cycles: float, phase: float = 0.0) -> 'FloatAnimation':
        """
        Return a triangle wave oscillating between min_val and max_val,
        starting at phase * 2π with cycles complete waves.

        :param min_val: Lowest value of the wave.
        :param max_val: Highest value of the wave.
        :param cycles: Number of complete oscillations.
        :param phase: Value from 0 to 1 of where to start the wave.
        """
        middle_val = (min_val + max_val) / 2
        amplitude = (max_val - min_val) / 2
        rate = Rate(lambda t: (
                middle_val +
                2 * amplitude * arcsin(
                    sin((2 * pi * t * cycles) - (2 * pi * phase))
                ) / pi
        ))
        return FloatAnimation(rate=rate)

    @classmethod
    def rotation(cls, cycles: float,
                 clockwise: bool = True,
                 phase: Optional[float] = 0.0):
        """
        Return a rotation in degrees.

        :param cycles: Number of complete rotations.
        :param clockwise: Rotate clockwise if True.
        :param phase: Starting phase between 0.0 and 1.0.
        """
        if clockwise:
            multiplier = -1
        else:
            multiplier = 1
        return FloatAnimation(rate=Rate(
            lambda t: (phase * 360) + multiplier * t * cycles * 360
        ))

    def at(self, t: float) -> float:

        for i in range(len(self.t)):
            if self.t[i + 1] >= t:
                dt = self.rate(
                    (t - self.t[i]) /
                    (self.t[i + 1] - self.t[i])
                )
                return (
                    self.values[i] +
                    (self.values[i + 1] - self.values[i]) * dt
                )
