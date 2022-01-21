from typing import List

from matplotlib.patches import Arc

from mpl_format.patches import PatchListFormatter


class ArcListFormatter(PatchListFormatter):

    _patches: List[Arc]

    def __init__(self, patches: List[Arc]):

        super().__init__(patches)

    def x_centers(self) -> List[float]:

        return [arc.get_center()[0] for arc in self._patches]

    def y_centers(self) -> List[float]:

        return [arc.get_center()[1] for arc in self._patches]

    def widths(self) -> List[float]:

        return [arc.width for arc in self._patches]

    def heights(self) -> List[float]:

        return [arc.height for arc in self._patches]

    def angles(self) -> List[float]:

        return [arc.angle for arc in self._patches]

    def theta_starts(self) -> List[float]:

        return [arc.theta1 for arc in self._patches]

    def theta_ends(self) -> List[float]:

        return [arc.theta2 for arc in self._patches]
