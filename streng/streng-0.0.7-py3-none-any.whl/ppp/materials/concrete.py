import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class KapposConfined91:
    fc: float
    εco: float
    ρw: float
    bc: float
    s: float
    fyw: float
    hoops_pattern: int  # (1=single,2=double,3=multi)

    def __post_init__(self):
        if self.hoops_pattern == 1:
            α = 0.55
            b = 0.75
        elif self.hoops_pattern == 2:
            α = 1.0
            b = 1.0
        elif self.hoops_pattern == 3:
            α = 1.25
            b = 1.0
        else:
            print('Check hoops pattern!')

        ωw = self.ρw * self.fyw / self.fc
        k = 1 + α * ωw**b

        self.fcc = k * self.fc
        self.εcco = k * k * self.εco
        self.u = 0.50 / ((0.75 * self.ρw * (self.bc / self.s)**0.5) +
                         (3 + 0.29 * (self.fc / k)) / (145 * (self.fc / k) - 1000.) - self.εco)


    def σc(self, εc):
        if εc <= self.εcco:
            return self.fcc * (2 * (εc / self.εcco) - (εc / self.εcco)**2)
        if εc > self.εcco:
            return max(self.fcc * (1 - self.u * (εc - self.εcco)), 0.25 * self.fcc)
