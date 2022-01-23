from pyelectric.electronic.amplifier import Amplifier as _Amplifier

from . import drawing
from .input import Input
from .output import Output


class Amplifier(_Amplifier):
    input: Input = Input(0, 0, 0, 0, 0)
    output: Output = Output(0, 0, 0, 0)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.input = Input(*args, **kwargs)

    def __call__(self) -> Output:
        Vcc = self.input.Vcc
        beta = self.input.beta
        ro = self.input.ro
        Rb = self.input.Rb
        Rc = self.input.Rc

        Ibq = (Vcc - 0.7)/Rb
        Ieq = (self.input.beta + 1)*Ibq

        re = 26e-3/Ieq
        Zi = 1/((1/Rb) + (1/(beta*re)))
        Zo = 1/((1/Rc) + (1/ro))
        Avnl = -Zo/re
        return Output(re, Zi, Zo, Avnl)

    @staticmethod
    def draw_void():
        return drawing.draw_void()

    def draw(self):
        return drawing.draw(self.input)
