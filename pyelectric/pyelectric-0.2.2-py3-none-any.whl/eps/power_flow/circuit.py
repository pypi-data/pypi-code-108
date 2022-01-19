from typing import List

import numpy as np

from .bar import Bar
from .bar.load_bar import LoadBar
from .bar.regulator_bar import RegulatorBar
from .bar.slack_bar import SlackBar
from .line import Line


class Circuit:
    bars: List[Bar]
    lines: List[Line]
    power_base: float
    __y_bus_array: np.ndarray
    __voltage_array: np.ndarray
    __power_esp_array: np.ndarray

    def __init__(self, bars: List[Bar], lines: List[Line], power_base: float = 1):
        self.bars = bars
        self.lines = lines
        self.power_base = power_base
        self.__y_bus_array = self.get_y_bus_array()
        self.__voltage_array = self.get_voltage_array()
        self.__power_esp_array = self.get_power_esp_array()

    def __str__(self) -> str:
        return '\n'.join([str(bar) for bar in self.bars])

    def get_bar_index(self, bar: Bar) -> int:
        for i, b in enumerate(self.bars):
            if b == bar:
                return i
        raise ValueError(f'Bar {bar} not found')

    def get_y_bus_array(self) -> np.ndarray:
        y_bus = np.zeros((len(self.bars), len(self.bars)), dtype=complex)
        for line in self.lines:
            bar1_index = self.get_bar_index(line.bar1)
            bar2_index = self.get_bar_index(line.bar2)
            y_bus[bar1_index, bar2_index] = -line.admittance
            y_bus[bar2_index, bar1_index] = -line.admittance

            y_bus[bar1_index, bar1_index] = sum(
                [l.admittance for l in self.lines if l.bar1 == line.bar1 or l.bar2 == line.bar1])

            y_bus[bar2_index, bar2_index] = sum(
                [l.admittance for l in self.lines if l.bar1 == line.bar2 or l.bar2 == line.bar2])

        return y_bus

    def get_power_esp_array(self) -> np.ndarray:
        power_g = np.zeros((len(self.bars)), dtype=complex)
        power_d = np.zeros((len(self.bars)), dtype=complex)
        for i, bar in enumerate(self.bars):
            if isinstance(bar, LoadBar):
                power_d[i] = bar.power
        power_esp = power_g - power_d
        return power_esp/self.power_base

    def get_voltage_array(self) -> np.ndarray:
        voltages = np.ones(len(self.bars), dtype=complex)
        for i in range(len(voltages)):
            if isinstance(self.bars[i], SlackBar):
                voltages[i] = self.bars[i].voltage
        return voltages

    def update_voltages(self, repeat: int = 1):
        for _ in range(repeat):
            y_bus = self.__y_bus_array
            power_esp = self.__power_esp_array
            voltages = self.__voltage_array

            for i, bar in enumerate(self.bars):
                if isinstance(bar, SlackBar):
                    continue
                I = power_esp[i].conjugate()/voltages[i].conjugate()
                summation = sum([y_bus[i, j]*voltages[j]
                                for j in range(len(voltages)) if i != j])
                voltages[i] = (I - summation)/y_bus[i, i]

            self.__voltage_array = voltages
            for i, bar in enumerate(self.bars):
                bar.voltage = voltages[i]
