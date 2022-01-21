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
        Vgg = self.input.Vgg
        Vp = self.input.Vp
        Idss = self.input.Idss
        rd = self.input.rd
        Rd = self.input.Rd
        Rg = self.input.Rg

        Vgs = -Vgg
        gm = (2*Idss/abs(Vp))*(1 - (Vgs/Vp))

        Zi = Rg
        Zo = 1/((1/rd) + (1/Rd))
        Avnl = -gm*Zo
        return Output(gm, Zi, Zo, Avnl)

    @staticmethod
    def draw_void():
        return drawing.draw_void()

    def draw(self):
        return drawing.draw(self.input)
