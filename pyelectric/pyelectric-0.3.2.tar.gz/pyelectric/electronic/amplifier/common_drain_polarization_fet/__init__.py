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
        Vdd = self.input.Vdd
        Rg = self.input.Rg
        Rs = self.input.Rs
        Vp = self.input.Vp
        Idss = self.input.Idss
        rd = self.input.rd
        Idq = self.input.Idq

        Vgs = ((Idq/Idss)**(1/2) - 1)*-Vp
        gm = (2*Idss/abs(Vp))*(1 - (Vgs/Vp))

        Zi = Rg
        Zo = 1/(1/Rs + 1/rd + gm)
        Req = gm/(1/rd + 1/Rs)
        Avnl = Req/(1 + Req)
        return Output(gm, Zi, Zo, Avnl)

    @staticmethod
    def draw_void():
        return drawing.draw_void()

    def draw(self):
        return drawing.draw(self.input)
