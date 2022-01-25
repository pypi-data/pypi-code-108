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
from vedo import Axes as vedo_axes_t
from vedo import Box as box_t
from vedo import Picture as picture_t
from vedo import Volume as volume_t
from vedo.shapes import Lines as lines_t
from vedo.shapes import Text3D as text_t

import cell_tracking_BC.in_out.graphics.dbe.vedo.style as styl
import cell_tracking_BC.in_out.graphics.generic.any_d as gnrc
from cell_tracking_BC.in_out.graphics.context import annotation_h
from cell_tracking_BC.in_out.graphics.context import axes_3d_t as base_axes_3d_t
from cell_tracking_BC.in_out.graphics.context import cell_annotation_h, colormap_h
from cell_tracking_BC.in_out.graphics.dbe.vedo.any_d import figure_t as figure_anyd_t


array_t = nmpy.ndarray


_MAX_N_TIME_LABELS = 15


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(figure_anyd_t, base_axes_3d_t):
    def SetTimeAxisProperties(self, latest: int, /) -> None:
        """"""
        origin, corner = self.bbox_origin_and_corner

        length, width, height = (_max - _min for _min, _max in zip(origin, corner))

        x_range, y_range, z_range = ((_min, _max) for _min, _max in zip(origin, corner))
        n_time_labels = min(latest + 1, _MAX_N_TIME_LABELS)
        time_labels = tuple(
            (_pos, _lbl)
            for _pos, _lbl in zip(
                nmpy.linspace(self.bbox[0][2], self.bbox[1][2], num=n_time_labels),
                nmpy.around(nmpy.linspace(0, latest, num=n_time_labels), decimals=1),
            )
        )

        box = box_t(pos=origin, length=length, width=width, height=height).alpha(0.1)
        axes = vedo_axes_t(
            box,
            xrange=x_range,
            yrange=y_range,
            zrange=z_range,
            zValuesAndLabels=time_labels,
            c="black",
        )

        self.__iadd__(axes)

    @staticmethod
    def TimeScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        size = 0.5 * sum(shape)

        return 2.0 * size / (length - 1)

    @staticmethod
    def MillefeuilleScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        size = 0.5 * sum(shape)

        return 0.1 * size

    def AddColormapFromMilestones(
        self,
        name: str,
        milestones: Sequence[Tuple[float, str]],
        /,
        *,
        position: str = "right",
    ) -> colormap_h:
        """"""
        # Leave it in 3-D (as opposed to any-D) because of 3-D box below
        output = lambda _vle: gnrc.ZeroOneValueToRGBAWithMilestones(
            _vle, milestones, clrs.getColor
        )

        discretized = tuple(
            output(_vle)[:3] for _vle in nmpy.linspace(0.0, 1.0, num=100)
        )
        box = box_t(pos=(0, 0, 0), length=10, width=10, height=10).alpha(0.0)
        box.cmap(discretized, box.points()[:, 2])
        box.addScalarBar(title=name, nlabels=0)

        self.__iadd__(box)

        return output

    def PlotLines(self, xs, ys, *args, zdir="z", **kwargs):
        """"""
        zs = args[0]

        if "color" in kwargs:
            color, alpha = gnrc.ColorAndAlpha(kwargs["color"], clrs.getColor)
        else:
            color, alpha = "black", None

        points = list(zip(ys, xs, zs))
        lines = lines_t(points[:-1], points[1:], c=color, lw=2)
        if alpha is not None:
            lines.alpha(alpha)

        self.__iadd__(lines)
        self.UpdateBBoxFromMany(ys, xs, zs)

    def PlotText(self, x, y, z, s, zdir=None, **kwargs):
        """"""
        position = [y, x, z]
        additionals = styl.ConvertedTextStyle(kwargs)
        if "alpha" in additionals:
            alpha = additionals["alpha"]
            del additionals["alpha"]
        else:
            alpha = None

        text = text_t(s, position, **additionals)
        if alpha is not None:
            text.alpha(alpha)

        text.followCamera()

        self.__iadd__(text)
        self.UpdateBBoxFromOne(position)

    def PlotCellAnnotation(
        self, position: Tuple[float, float, float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_h, Sequence[annotation_h]]:
        """"""
        additionals = kwargs.copy()
        if "alpha" in additionals:
            alpha = additionals["alpha"]
            del additionals["alpha"]
        else:
            alpha = None

        # TODO: multi-piece text is currently dealt with as single-piece text
        if not isinstance(text, str):
            text = "".join(_elm[0] for _elm in text)

        flipped = [position[1], position[0], position[2]]
        text = text_t(text, flipped, **additionals)
        if alpha is not None:
            text.alpha(alpha)
        text.followCamera()

        self.__iadd__(text)
        self.UpdateBBoxFromOne(flipped)

        return None

    def PlotImageInZ(
        self,
        image: array_t,
        all_rows: array_t,
        all_cols: array_t,
        n_levels: int,
        height: float,
        z_scaling: float,
        /,
        min_intensity: float = 0.0,
        intensity_range: float = 1.0,
        alpha: float = 0.8,
        **kwargs,
    ) -> None:
        """"""
        scaled = 255.0 * (image - min_intensity) / intensity_range
        picture = picture_t(scaled).z(z_scaling * height).alpha(alpha)

        self.__iadd__(picture)
        self.UpdateBBoxFromMany(all_cols.flatten(), all_rows.flatten(), (height,))

    def PlotIsosurface(
        self,
        volume: array_t,
        iso_value: float,
        /,
        should_be_capped: bool = False,
        keep_every: int = 2,
        **kwargs,
    ) -> None:
        """"""
        if should_be_capped:
            cap = nmpy.zeros_like(volume[0, ...])[None, ...]
            volume = nmpy.concatenate((cap, volume, cap), axis=0)

        isosurface = volume_t(volume).isosurface(threshold=[iso_value])
        time_scaling = self.__class__.TimeScaling(volume.shape[:2], volume.shape[2])
        isosurface.scale(s=(1.0, 1.0, time_scaling))

        self.__iadd__(isosurface)
        self.UpdateBBoxFromMany(
            isosurface.xbounds(), isosurface.ybounds(), isosurface.zbounds()
        )


axes_t = figure_t
