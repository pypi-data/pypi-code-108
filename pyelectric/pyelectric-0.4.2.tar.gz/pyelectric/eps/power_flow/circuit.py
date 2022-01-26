from typing import List

import numpy as np

from .bar import Bar
from .bar.load_bar import LoadBar
from .bar.regulator_bar import RegulatorBar
from .line import Line


class Circuit:
    __bars: List[Bar]
    __lines: List[Line]
    __power_base: float

    def __init__(self, bars: List[Bar], lines: List[Line], power_base: float = 1):
        self.__bars = bars
        self.__lines = lines
        self.__power_base = power_base
        self.bar_powers_to_pu()

    def __str__(self) -> str:
        bars = '\n'.join([str(bar) for bar in self.__bars])
        lines = '\n'.join([str(line) for line in self.__lines])
        return f'{bars}\n{lines}'

    @property
    def bars(self) -> List[Bar]:
        return self.__bars

    @property
    def lines(self) -> List[Line]:
        return self.__lines

    @property
    def power_base(self) -> float:
        return self.__power_base

    def bar_powers_to_pu(self):
        for bar in self.__bars:
            bar.power /= self.__power_base
            if isinstance(bar, RegulatorBar):
                bar.active_power /= self.__power_base
            elif isinstance(bar, LoadBar):
                bar.active_power /= self.__power_base
                bar.reactive_power /= self.__power_base

    def get_bar_index(self, bar: Bar) -> int:
        for i, b in enumerate(self.__bars):
            if b == bar:
                return i
        raise ValueError(f'Bar {bar} not found')

    def update_bar_voltages(self, voltage_array: np.ndarray):
        for i, bar in enumerate(self.__bars):
            bar.voltage = voltage_array[i]

    def update_bar_powers(self, power_array: np.ndarray):
        for i, bar in enumerate(self.__bars):
            bar.power = power_array[i]

    def update_line_amperages(self, amperage_array: np.ndarray):
        for line in self.__lines:
            bar1 = line.bar1
            bar2 = line.bar2
            bar1_index = self.get_bar_index(bar1)
            bar2_index = self.get_bar_index(bar2)
            line.amperage = amperage_array[bar1_index, bar2_index]

    def update_line_powers(self, power_array: np.ndarray):
        for line in self.__lines:
            bar1 = line.bar1
            bar2 = line.bar2
            bar1_index = self.get_bar_index(bar1)
            bar2_index = self.get_bar_index(bar2)
            line.power = power_array[bar1_index, bar2_index]
            line.power_reverse = power_array[bar2_index, bar1_index]
