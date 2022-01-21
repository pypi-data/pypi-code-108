import math
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
        self.bar_powers_to_pu()
        self.__y_bus_array = self.get_y_bus_array()
        self.__voltage_array = self.get_voltage_array()
        self.__power_esp_array = self.get_power_esp_array()

    def __str__(self) -> str:
        bars = '\n'.join([str(bar) for bar in self.bars])
        lines = '\n'.join([str(line) for line in self.lines])
        return f'{bars}\n{lines}'

    def bar_powers_to_pu(self):
        for bar in self.bars:
            bar.power /= self.power_base
            if isinstance(bar, RegulatorBar):
                bar.active_power /= self.power_base
            elif isinstance(bar, LoadBar):
                bar.active_power /= self.power_base
                bar.reactive_power /= self.power_base

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
            elif isinstance(bar, RegulatorBar):
                power_g[i] = bar.active_power
        power_esp = power_g - power_d
        return power_esp

    def get_voltage_array(self) -> np.ndarray:
        voltages = np.ones(len(self.bars), dtype=complex)
        for i, bar in enumerate(self.bars):
            if isinstance(bar, SlackBar):
                voltages[i] = bar.voltage
            elif isinstance(bar, RegulatorBar):
                voltages[i] = bar.voltage_module
        return voltages

    def get_bar_power(self, bar: Bar) -> complex:
        voltages = self.__voltage_array
        y_bus = self.__y_bus_array
        i = self.get_bar_index(bar)
        summation = sum([y_bus[i, j]*voltages[j]
                        for j in range(len(voltages)) if i != j])
        S = (voltages[i].conjugate()*(y_bus[i, i]
             * voltages[i] + summation)).conjugate()
        return S

    def get_bar_voltage(self, bar: Bar) -> complex:
        voltages = self.__voltage_array
        y_bus = self.__y_bus_array
        power_esp = self.__power_esp_array
        i = self.get_bar_index(bar)
        I = power_esp[i].conjugate()/voltages[i].conjugate()
        summation = sum([y_bus[i, j]*voltages[j]
                        for j in range(len(voltages)) if i != j])
        V = (I - summation)/y_bus[i, i]
        return V

    def solve(self, repeat: int = 1):
        for _ in range(repeat):
            self.update_bar_voltages()
        self.update_bar_powers()
        self.update_line_amperages()
        self.update_line_powers()

    def update_bar_voltages(self):
        voltages = self.__voltage_array
        power_esp = self.__power_esp_array

        for i, bar in enumerate(self.bars):
            if isinstance(bar, LoadBar):
                voltages[i] = self.get_bar_voltage(bar)
            elif isinstance(bar, RegulatorBar):
                Q = self.get_bar_power(bar).imag
                P = power_esp[i].real
                power_esp[i] = P + 1j*Q
                V = self.get_bar_voltage(bar)
                V_real = math.sqrt(bar.voltage_module**2 - V.imag**2)
                voltages[i] = V_real + V.imag*1j

        self.__voltage_array = voltages
        for i, bar in enumerate(self.bars):
            bar.voltage = voltages[i]

    def update_bar_powers(self):
        for i, bar in enumerate(self.bars):
            if isinstance(bar, SlackBar):
                bar.power = self.get_bar_power(bar)
            elif isinstance(bar, RegulatorBar):
                bar.power = self.__power_esp_array[i]

    def update_line_amperages(self):
        y_bus = self.__y_bus_array
        y = y_bus*(np.identity(len(y_bus))*2 - 1)
        for line in self.lines:
            bar1 = line.bar1
            bar2 = line.bar2
            bar1_index = self.get_bar_index(bar1)
            bar2_index = self.get_bar_index(bar2)
            I = (bar1.voltage - bar2.voltage)*y[bar1_index, bar2_index]
            line.amperage = I

    def update_line_powers(self):
        for line in self.lines:
            I = line.amperage

            V1 = line.bar1.voltage
            S12 = V1*I.conjugate()
            line.power = S12

            V2 = line.bar2.voltage
            S21 = V2*(-I).conjugate()
            line.power_reverse = S21
