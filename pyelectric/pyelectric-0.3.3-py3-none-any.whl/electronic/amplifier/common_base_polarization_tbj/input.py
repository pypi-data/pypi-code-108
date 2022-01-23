from typing import List

from pyelectric.electronic.amplifier.input import Input as _Input


class Input(_Input):
    Vcc: float
    R1: float
    R2: float
    Re: float
    beta: float
    ro: float

    def __init__(self, Vcc: float, R1: float, R2: float, Re: float, beta: float, ro: float) -> None:
        super().__init__()
        self.Vcc = Vcc
        self.R1 = R1
        self.R2 = R2
        self.Re = Re
        self.beta = beta
        self.ro = ro

    @staticmethod
    def get_parameter_names() -> List[str]:
        return ['Vcc', 'beta', 'ro', 'R1', 'R2', 'Re']
