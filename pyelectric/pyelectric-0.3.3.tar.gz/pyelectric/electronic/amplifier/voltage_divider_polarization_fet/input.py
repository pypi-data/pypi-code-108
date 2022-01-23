from typing import List

from pyelectric.electronic.amplifier.input import Input as _Input


class Input(_Input):
    Vdd: float
    R1: float
    R2: float
    Rd: float
    Rs: float
    Vp: float
    Idss: float
    rd: float

    def __init__(self, Vdd: float, R1: float, R2: float, Rd: float, Rs: float, Vp: float, Idss: float, rd: float) -> None:
        self.Vdd = Vdd
        self.R1 = R1
        self.R2 = R2
        self.Rd = Rd
        self.Rs = Rs
        self.Vp = Vp
        self.Idss = Idss
        self.rd = rd

    @staticmethod
    def get_parameter_names() -> List[str]:
        return ['Vdd', 'Vp', 'Idss', 'rd', 'R1', 'R2', 'Rd', 'Rs']
