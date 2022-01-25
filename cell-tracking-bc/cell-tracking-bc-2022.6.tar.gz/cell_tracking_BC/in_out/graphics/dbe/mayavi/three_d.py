# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from __future__ import annotations

import dataclasses as dtcl
from typing import Sequence, Tuple, Union

import numpy as nmpy
import vedo.colors as clrs
from mayavi import mlab

import cell_tracking_BC.in_out.graphics.dbe.mayavi.style as styl
import cell_tracking_BC.in_out.graphics.generic.any_d as gnrc
from cell_tracking_BC.in_out.graphics.context import axes_3d_t as abstract_axes_3d_t
from cell_tracking_BC.in_out.graphics.context import colormap_h
from cell_tracking_BC.in_out.graphics.dbe.mayavi.any_d import figure_t as base_figure_t


array_t = nmpy.ndarray


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(base_figure_t, abstract_axes_3d_t):
    @classmethod
    def NewFigureAndAxes(
        cls, /, *, n_rows: int = 1, n_cols: int = 1, title: str = None
    ) -> Tuple[figure_t, Union[axes_t, Sequence[axes_t], Sequence[Sequence[axes_t]]],]:
        """"""
        figure = cls(figure=title, bgcolor=(1, 1, 1))
        axes = figure

        mlab.axes(
            xlabel="row positions",
            ylabel="column positions",
            zlabel="time points",
            figure=figure,
        )
        mlab.outline(figure=figure)

        return figure, axes

    @staticmethod
    def TimeScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        size = 0.5 * sum(shape)

        return size / length

    @staticmethod
    def MillefeuilleScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        size = 0.5 * sum(shape)

        return size / length

    def AddColormapFromMilestones(
        self,
        name: str,
        milestones: Sequence[Tuple[float, str]],
        /,
        *,
        position: str = "right",
    ) -> colormap_h:
        """"""
        output = lambda _vle: gnrc.ZeroOneValueToRGBAWithMilestones(
            _vle, milestones, clrs.getColor
        )

        return output

    def PlotLines(self, xs, ys, *args, zdir="z", **kwargs):
        """"""
        zs = args[0]

        if "color" in kwargs:
            color, _ = gnrc.ColorAndAlpha(kwargs["color"], clrs.getColor)
        else:
            color = "black"

        # tube_radius=0.025*size
        mlab.plot3d(xs, ys, zs, color=color, figure=self)

    def PlotText(self, x, y, z, s, zdir=None, **kwargs):
        """"""
        mlab.text3d(
            x,
            y,
            z,
            s,
            figure=self,
            **styl.ConvertedTextStyle(kwargs),
        )


axes_t = figure_t
