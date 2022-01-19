from typing import Union, List

from celluloid import Camera
from numpy import linspace

from mpl_format.animation.shapes.base import ShapeAnimation
from mpl_format.axes import AxesFormatter
from mpl_format.figures import FigureFormatter


class AxesAnimator(object):

    def __init__(self,
                 formatter: Union[AxesFormatter, FigureFormatter],
                 duration: float):

        self.formatter: AxesFormatter = formatter or AxesFormatter()
        self.duration: float = duration
        self.shapes: List[ShapeAnimation] = []

    def add_animation(self, animation: ShapeAnimation):

        self.shapes.append(animation)

    def animate(self, file_name: str, fps: float = 30):

        camera = Camera(self.formatter.axes.figure)
        for t in linspace(
                0, self.duration, 1 + int(self.duration * fps)
        ):
            for shape in self.shapes:
                shape.draw(t / self.duration, axes=self.formatter)
            camera.snap()
        animation = camera.animate()
        animation.save(file_name, writer='imagemagick', fps=30)
