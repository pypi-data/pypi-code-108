from __future__ import annotations

import cmath
import math
from typing import Union

from pyelectric.ac.phasor import Phasor


class Power:
    complex_power: complex
    factor: float
    is_late: bool
    phase: float

    def __init__(
        self,
        complex_power: Union[complex, Phasor] = None, *,
        active: float = None,
        reactive: float = None,
        factor: float = None,
        apparent: float = None,
        is_late: bool = None,
    ) -> None:
        if factor == 1:
            is_late = False
        if complex_power is not None:
            if isinstance(complex_power, Phasor):
                complex_power = complex_power.value
            self.complex_power = complex_power
        elif (active, reactive).count(None) == 0:
            self.complex_power = complex(active, reactive)
        elif (factor, apparent, is_late).count(None) == 0:
            theta = math.acos(factor)
            P, Q = apparent*math.cos(theta), apparent*math.sin(theta)
            self.complex_power = complex(P, Q if is_late else -Q)
        elif (active, apparent, is_late).count(None) == 0:
            P, Q = active, apparent*math.sin(math.acos(active/apparent))
            self.complex_power = complex(P, Q if is_late else -Q)
        elif (reactive, apparent, is_late).count(None) == 0:
            theta = math.asin(reactive/apparent)
            P, Q = apparent*math.cos(theta), reactive
            self.complex_power = complex(P, Q if is_late else -Q)
        elif (active, factor, is_late).count(None) == 0:
            theta = math.acos(factor)
            apparent = active/factor
            P, Q = active, apparent*math.sin(theta)
            self.complex_power = complex(P, Q if is_late else -Q)
        elif (reactive, factor, is_late).count(None) == 0:
            theta = math.acos(factor)
            apparent = reactive/math.sin(theta)
            P, Q = apparent*math.cos(theta), reactive
            self.complex_power = complex(P, Q if is_late else -Q)
        else:
            raise ValueError('insufficient power information')

    @property
    def active(self) -> float:
        return self.complex_power.real

    @property
    def reactive(self) -> float:
        return self.complex_power.imag

    @property
    def apparent(self) -> float:
        return math.sqrt(self.active**2 + self.reactive**2)

    @property
    def factor(self) -> float:
        return self.active/self.apparent

    @property
    def is_late(self) -> bool:
        return self.reactive > 0

    @property
    def phase(self) -> float:
        return cmath.phase(self.complex_power)

    def print_powers(self) -> None:
        print(f'Active: {self.active:.2f}')
        print(f'Reactive: {self.reactive:.2f}')
        print(f'Apparent: {self.apparent:.2f}')
        print(f'Factor: {self.factor:.2f}')
        print(f'Phase: {math.degrees(self.phase):.2f}°')
        print(f'Is late: {self.is_late}')

    def __str__(self) -> str:
        return f'{self.active:.2f} + {self.reactive:.2f}j'

    def __repr__(self) -> str:
        return self.__str__()

    def __mod__(self, other: Power) -> Power:
        return Power(self.complex_power % other.complex_power)

    def __add__(self, other: Union[Power, Phasor, float]) -> Power:
        if isinstance(other, Power):
            return Power(self.complex_power + other.complex_power)
        elif isinstance(other, Phasor):
            return Power(self.complex_power + other.value)
        else:
            return Power(self.complex_power + other)

    def __sub__(self, other: Union[Power, Phasor, float]) -> Power:
        if isinstance(other, Power):
            return Power(self.complex_power - other.complex_power)
        elif isinstance(other, Phasor):
            return Power(self.complex_power - other.value)
        else:
            return Power(self.complex_power - other)

    def __mul__(self, other: Union[Power, Phasor, float]) -> Power:
        if isinstance(other, Power):
            return Power(self.complex_power * other.complex_power)
        elif isinstance(other, Phasor):
            return Power(self.complex_power * other.value)
        else:
            return Power(self.complex_power * other)

    def __truediv__(self, other: Union[Power, Phasor, float]) -> Power:
        if isinstance(other, Power):
            return Power(self.complex_power / other.complex_power)
        elif isinstance(other, Phasor):
            return Power(self.complex_power / other.value)
        else:
            return Power(self.complex_power / other)
