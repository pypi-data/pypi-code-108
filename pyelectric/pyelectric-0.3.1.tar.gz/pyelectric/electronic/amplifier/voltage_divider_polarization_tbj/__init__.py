from pyelectric.electronic.amplifier import Amplifier as _Amplifier

from . import drawing
from .input import Input
from .output import Output


class Amplifier(_Amplifier):
    input: Input = Input(0, 0, 0, 0, 0, 0, 0)
    output: Output = Output(0, 0, 0, 0)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.input = Input(*args, **kwargs)

    def __call__(self) -> Output:
        Vcc = self.input.Vcc
        beta = self.input.beta
        ro = self.input.ro
        R1 = self.input.R1
        R2 = self.input.R2
        Rc = self.input.Rc
        Re = self.input.Re

        R_line = 1/((1/R1) + (1/R2))
        Vb = Vcc*R2/(R1 + R2)
        Vbe = 0.7
        Ve = Vb - Vbe
        Ieq = Ve/Re

        Zo = 1/((1/ro) + (1/Rc))
        re = 26e-3/Ieq
        Zi = 1/((1/R_line) + (1/(beta*re)))
        Avnl = -Zo/re

        return Output(re, Zi, Zo, Avnl)

    @staticmethod
    def draw_void():
        return drawing.draw_void()

    def draw(self):
        return drawing.draw(self.input)
