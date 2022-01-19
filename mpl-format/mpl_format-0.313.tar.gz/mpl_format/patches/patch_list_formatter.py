from matplotlib.patches import Patch
from typing import List, Iterable

from mpl_format.compound_types import Color


class PatchListFormatter(object):

    def __init__(self, patches: List[Patch]):

        self._patches: List[Patch] = patches

    @property
    def edge_colors(self) -> List[Color]:
        """
        Return the edge-colors of each patch.
        """
        return [patch.get_edgecolor()
                for patch in self._patches]

    @edge_colors.setter
    def edge_colors(self, values: Iterable[Color]):
        """
        Set the edge-colors of each patch.

        :param values: List of colors.
        """
        for patch, color in zip(self._patches, values):
            patch.set_edgecolor(color)

    @property
    def face_colors(self) -> List[Color]:
        """
        Return the face-colors of each patch.
        """
        return [patch.get_facecolor()
                for patch in self._patches]

    @face_colors.setter
    def face_colors(self, values: Iterable[Color]):
        """
        Set the face-colors of each patch.

        :param values: List of colors.
        """
        for patch, color in zip(self._patches, values):
            patch.set_facecolor(color)

    @property
    def alphas(self) -> List[float]:
        """
        Return the alphas of each patch.
        """
        return [patch.get_alpha()
                for patch in self._patches]

    @alphas.setter
    def alphas(self, values: Iterable[float]):
        """
        Set the alphas of each patch.

        :param values: List of alphas.
        """
        for patch, alpha in zip(self._patches, values):
            patch.set_alpha(alpha)

    @property
    def line_styles(self) -> List[str]:
        """
        Return the line-styles of each patch.
        """
        return [patch.get_linestyle()
                for patch in self._patches]

    @line_styles.setter
    def line_styles(self, values: Iterable[str]):
        """
        Set the line-styles of each patch.

        :param values:  List of line-styles.
        """
        for patch, line_style in zip(self._patches, values):
            patch.set_linestyle(line_style)

    @property
    def line_widths(self) -> List[float]:
        """
        Return the line-widths of each patch.
        """
        return [patch.get_linewidth()
                for patch in self._patches]

    @line_widths.setter
    def line_widths(self, values: Iterable[float]):
        """
        Set the line-widths of each patch.

        :param values:  List of line-widths.
        """
        for patch, line_width in zip(self._patches, values):
            patch.set_linewidth(line_width)
