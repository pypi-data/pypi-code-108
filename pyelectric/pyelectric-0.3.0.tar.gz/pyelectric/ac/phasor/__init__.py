from __future__ import annotations

import cmath
import math
from typing import Union


class Phasor:
    value: complex
    decimal_places: int = 2
    angle_in_degree: bool = True

    def __init__(self, r: Union[float, complex], theta: float = None) -> None:
        if theta is None:
            r, theta = cmath.polar(r)
        self.value = cmath.rect(r, theta)

    @property
    def abs(self):
        return abs(self.value)

    @property
    def phase(self):
        return cmath.phase(self.value)

    @abs.setter
    def abs(self, value: float):
        self.value = cmath.rect(value, self.phase)

    @phase.setter
    def phase(self, value: float):
        self.value = cmath.rect(self.abs, value)

    def conjugate(self) -> Phasor:
        return Phasor(self.value.conjugate())

    def __str__(self) -> str:
        r, theta = cmath.polar(self.value)
        r = round(r, self.decimal_places)
        if self.angle_in_degree:
            theta = math.degrees(theta)
            theta = round(theta, self.decimal_places)
            return f"{r} ∠ {theta}°"
        theta = round(theta, self.decimal_places)
        return f"{r} ∠ {theta}"

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(self.value + (other.value if isinstance(other, Phasor) else other))

    def __sub__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(self.value - (other.value if isinstance(other, Phasor) else other))

    def __mul__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(self.value * (other.value if isinstance(other, Phasor) else other))

    def __truediv__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(self.value / (other.value if isinstance(other, Phasor) else other))

    def __pow__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(self.value ** (other.value if isinstance(other, Phasor) else other))

    def __floordiv__(self, other: Union[Phasor, complex]) -> Phasor:
        return Phasor(1 / ((1 / self.value) + (1 / other.value if isinstance(other, Phasor) else other)))

    def __eq__(self, other: Union[Phasor, complex]) -> bool:
        return self.value == (other.value if isinstance(other, Phasor) else other)
