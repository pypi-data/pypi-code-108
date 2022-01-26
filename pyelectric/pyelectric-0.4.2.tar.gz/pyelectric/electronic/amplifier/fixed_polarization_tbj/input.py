from typing import List

from pyelectric.electronic.amplifier.input import Input as _Input


class Input(_Input):
    Vcc: float
    Rc: float
    beta: float
    ro: float
    Rb: float

    def __init__(self, Vcc: float, Rc: float, beta: float, ro: float, Rb: float) -> None:
        self.Vcc = Vcc
        self.Rc = Rc
        self.beta = beta
        self.ro = ro
        self.Rb = Rb

    @staticmethod
    def get_parameter_names() -> List[str]:
        return ['Vcc', 'beta', 'ro', 'Rb', 'Rc']
