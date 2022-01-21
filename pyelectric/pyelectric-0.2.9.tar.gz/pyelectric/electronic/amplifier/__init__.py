from abc import ABC, abstractmethod, abstractstaticmethod

from schemdraw import Drawing

from . import drawing
from .input import Input
from .output import Output


class Amplifier(ABC):
    input: Input
    output: Output

    @abstractstaticmethod
    def draw_void() -> Drawing:
        pass

    @abstractmethod
    def draw(self) -> Drawing:
        pass

    def draw_equivalent(self) -> Drawing:
        output = self()
        return drawing.draw_equivalent_model(output)

    def draw_equivalent_void(self) -> Drawing:
        return drawing.draw_equivalent_model_void()

    @abstractmethod
    def __call__(self) -> Output:
        pass
