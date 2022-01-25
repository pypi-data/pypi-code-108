"""

    .. uml::

        class LongReinforcementLayer <<(C,#FF7700)>> {
            .. class atributes ..
            - __cached_props_list: list
            .. attributes ..
            + ns: list
            + dias: list
            + units_input: string
            + units_output: string
            .. properties ..
            - length_multiplier_input
            - length_multiplier_output
            .. cached_properties ..
            + Astot: float
            + ntot: float
            + dia_min: float
            + dia_max: float
            + dia_equiv: float
            + As_equiv: float
            .. methods ..
            - invalidate_cache()
        }

        class TransReinforcementLayer <<(C,#FF7700)>> {
            vlivli
        }


"""

from cached_property import cached_property
from typing import List
import numpy as np
from streng.ppp.sections.concrete.reinforcement.areas import As_layer


class LongReinforcementLayer:
    __cached_props_list = ['Astot', 'ntot', 'dia_max', 'dia_min', 'dia_equiv', 'As_equiv']

    def __init__(self, ns: List[float], dias: List[float], units_input='mm', units_output='mm'):
        self.ns = ns
        self.dias = dias
        self.units_input = units_input
        self.units_output = units_output

    def invalidate_cache(self, keys_list: List[str]):
        for key in keys_list:
            if key in self.__dict__.keys():
                del self.__dict__[key]

    @property
    def ns(self) -> List[float]:
        return self._ns

    @ns.setter
    def ns(self, value: List[float]):
        self.invalidate_cache(self.__cached_props_list)
        self._ns = value

    @property
    def dias(self) -> List[float]:
        return self._dias * np.array([self.length_multiplier_input])

    @dias.setter
    def dias(self, value: List[float]):
        self.invalidate_cache(self.__cached_props_list)
        self._dias = value

    @property
    def length_multiplier_input(self) -> float:
        if self.units_input == 'm':
            return 1000.
        elif self.units_input == 'cm':
            return 10.
        else:
            return 1.

    @property
    def length_multiplier_output(self) -> float:
        if self.units_output == 'm':
            return 0.001
        elif self.units_output == 'cm':
            return 0.1
        else:
            return 1.

    @cached_property
    def Astot(self) -> float:
        return As_layer(self.ns, self.dias) * self.length_multiplier_output ** 2

    @cached_property
    def ntot(self) -> float:
        return sum(self.ns)

    @cached_property
    def dia_max(self) -> float:
        return max(self.dias) * self.length_multiplier_output

    @cached_property
    def dia_min(self) -> float:
        return min(self.dias) * self.length_multiplier_output

    @cached_property
    def dia_equiv(self) -> float:
        if self.ntot > 0:
            return np.sqrt(4 * self.Astot / (self.ntot * np.pi))
        else:
            return 0.0

    @cached_property
    def As_equiv(self) -> float:
        return np.pi * self.dia_equiv ** 2 / 4

    @classmethod
    def from_string(cls, reinf_string: str, units_input='mm', units_output='mm', dia_symbol='Φ'):
        ns_and_dias = [x.split(dia_symbol) for x in reinf_string.split('+')]
        ns = [float(y[0]) for y in ns_and_dias]
        dias = [float(y[1]) for y in ns_and_dias]

        return cls(ns, [d for d in dias], units_input, units_output)


class TransReinforcementLayer:
    __cached_props_list = ['As']

    def __init__(self, n: float, dia: float, s: float, units_input='mm', units_output='mm'):
        self.n = n
        self.dia = dia
        self.s = s
        self.units_input = units_input
        self.units_output = units_output
        self.dia_symbol = dia_symbol

    def invalidate_cache(self, keys_list: List[str]):
        for key in keys_list:
            if key in self.__dict__.keys():
                del self.__dict__[key]

    @property
    def n(self) -> float:
        return self._n

    @n.setter
    def n(self, value: float):
        self.invalidate_cache(self.__cached_props_list)
        self._n = value

    @property
    def dia(self) -> float:
        return self._dia * self.length_multiplier_input

    @dia.setter
    def dia(self, value: float):
        self.invalidate_cache(self.__cached_props_list)
        self._dia = value

    @property
    def s(self) -> float:
        return self._s * self.length_multiplier_input

    @s.setter
    def s(self, value: float):
        self.invalidate_cache(self.__cached_props_list)
        self._s = value

    @property
    def length_multiplier_input(self) -> float:
        if self.units_input == 'm':
            return 1000.
        elif self.units_input == 'cm':
            return 10.
        else:
            return 1.

    @property
    def length_multiplier_output(self) -> float:
        if self.units_output == 'm':
            return 0.001
        elif self.units_output == 'cm':
            return 0.1
        else:
            return 1.

    @cached_property
    def As(self) -> float:
        return As_layer(self.n, self.dia) * self.length_multiplier_output ** 2

    @classmethod
    def from_string(cls, reinf_string, units_input='mm', units_output='mm', dia_symbol='Φ'):
        # Πχ reinf_string='Φ8/140(3)'

        n = int(reinf_string[reinf_string.find("(") + 1:reinf_string.find(")")])
        dia = float(reinf_string[reinf_string.find(
            dia_symbol) + 1:reinf_string.find("/")])
        s = float(reinf_string[reinf_string.find(
            "/") + 1:reinf_string.find("(")])

        return cls(n, dia, s, units_input, units_output)
