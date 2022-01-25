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

import matplotlib.pyplot as pypl
import numpy as nmpy
import scipy.interpolate as ntrp
import skimage.measure as msre
from matplotlib.text import Annotation as annotation_t
from mpl_toolkits.mplot3d import Axes3D as pypl_axes_t

from cell_tracking_BC.in_out.graphics.context import axes_3d_t as base_axes_3d_t
from cell_tracking_BC.in_out.graphics.context import cell_annotation_h
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.any_d import axes_t as axes_anyd_t
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.any_d import (
    figure_t as figure_anyd_t,
)


array_t = nmpy.ndarray


_MC_STEP_SIZE = 5  # MC=marching cubes
_MIN_MC_TIME_STEPS = 3


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_t(pypl_axes_t, axes_anyd_t, base_axes_3d_t):

    name = "ctBC_three_d_axes"
    PlotPoints = pypl_axes_t.scatter
    PlotLines = pypl_axes_t.plot
    PlotText = pypl_axes_t.text

    def SetTimeAxisProperties(self, latest: int, /) -> None:
        """"""
        self.set_zlim(0, latest)

        n_ticks = min(20, latest + 1)
        self.set_zticks(nmpy.linspace(0.0, latest, num=n_ticks))
        self.set_zticklabels(
            str(round(latest * _idx / (n_ticks - 1), 1)) for _idx in range(n_ticks)
        )

    def PlotCellAnnotation(
        self, position: Tuple[float, float, float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_t, Sequence[annotation_t]]:
        """"""
        # TODO: multi-piece text is currently dealt with as single-piece text
        if not isinstance(text, str):
            text = "".join(_elm[0] for _elm in text)

        # annotate: only for 2-D; use text instead in 3-D
        output = self.text(*position, text, **kwargs)

        return output

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
        self.contourf(
            all_rows,
            all_cols,
            image,
            levels=n_levels,
            offset=height,
            alpha=alpha,
            **kwargs,
        )

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
        n_frames_all = volume.shape[0]
        n_frames_kept = int((n_frames_all - 1) / keep_every) + 1
        frame_shape = volume.shape[1:]

        original_extents = (
            range(n_frames_all),
            range(frame_shape[0]),
            range(frame_shape[1]),
        )
        interpolated_extents = (
            nmpy.linspace(
                0,
                n_frames_all - ((n_frames_all - 1) % keep_every) - 1,
                num=n_frames_kept,
            ),
            *original_extents[1:],
        )
        all_times, all_rows, all_cols = nmpy.meshgrid(
            *interpolated_extents, indexing="ij"
        )
        interpolated_sites = nmpy.vstack(
            (all_times.flat, all_rows.flat, all_cols.flat)
        ).T
        interpolated = ntrp.interpn(original_extents, volume, interpolated_sites)

        reshaped = nmpy.reshape(interpolated, (n_frames_kept, *frame_shape))
        reorganized = nmpy.moveaxis(reshaped, (0, 1, 2), (2, 0, 1))
        flipped = nmpy.flip(reorganized, axis=2)
        if should_be_capped:
            cap = nmpy.zeros_like(flipped[..., 0])[..., None]
            flipped = nmpy.dstack((cap, flipped, cap))

        if n_frames_kept / _MC_STEP_SIZE < _MIN_MC_TIME_STEPS:
            step_size = max(1, int(round(n_frames_kept / _MIN_MC_TIME_STEPS)))
        else:
            step_size = _MC_STEP_SIZE
        try:
            vertices, faces, *_ = msre.marching_cubes(
                flipped, iso_value, step_size=step_size
            )
        except RuntimeError as exception:
            print(
                f"{self.__class__.PlotIsosurface.__name__}: Error in {iso_value}-isosurface extraction "
                f"in volume with min {nmpy.amin(flipped)} and max {nmpy.amax(flipped)} "
                f"with step size {step_size}\n{exception}"
            )
            return

        vertices[:, 2] *= keep_every
        self.plot_trisurf(
            vertices[:, 0],
            vertices[:, 1],
            faces,
            nmpy.amax(vertices[:, 2]) - vertices[:, 2],
            **kwargs,
        )


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(figure_anyd_t):
    @classmethod
    def NewFigureAndAxes(
        cls, /, *, n_rows: int = 1, n_cols: int = 1, title: str = None
    ) -> Tuple[figure_t, Union[axes_t, Sequence[axes_t], Sequence[Sequence[axes_t]]],]:
        """"""
        figure = pypl.figure(FigureClass=cls)
        axes = axes_t(figure, auto_add_to_figure=False)
        figure.add_axes(axes)

        if title is not None:
            axes.set_title(title)
        axes.set_xlabel("row positions")
        axes.set_ylabel("column positions")
        axes.set_zlabel("time points")

        return figure, axes
