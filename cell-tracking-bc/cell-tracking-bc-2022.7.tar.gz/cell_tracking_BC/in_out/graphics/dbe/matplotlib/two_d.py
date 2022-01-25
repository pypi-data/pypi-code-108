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

import matplotlib.projections as prjs
import matplotlib.pyplot as pypl
from matplotlib import rc as SetMatplotlibConfig
from matplotlib import transforms as trsf
from matplotlib.backend_bases import MouseEvent as mouse_event_t
from matplotlib.image import AxesImage as axes_image_t
from matplotlib.text import Annotation as annotation_t
from numpy import ndarray as array_t

from cell_tracking_BC.in_out.graphics.context import (
    axes_2d_t as base_axes_2d_t,
    cell_annotation_h,
)
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.any_d import axes_t as axes_anyd_t
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.any_d import (
    figure_t as figure_anyd_t,
)
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.style import (
    CELL_ANNOTATION_BBOX_STYLE_DEFAULT,
    CELL_ANNOTATION_BBOX_STYLE_HIGHLIGHT,
    CELL_ANNOTATION_COLOR_DEFAULT,
    CELL_ANNOTATION_COLOR_HIGHLIGHT,
)
from cell_tracking_BC.in_out.graphics.generic.two_d_sequence import (
    s_viewer_2d_t as base_s_viewer_2d_t,
)
from cell_tracking_BC.in_out.graphics.generic.two_d_tracking import (
    t_viewer_2d_t as base_t_viewer_2d_t,
)


pypl_axes_t = pypl.Axes


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_t(axes_anyd_t, base_axes_2d_t):

    name = "ctBC_two_d_axes"
    __image__: axes_image_t = None
    PlotPoints = pypl_axes_t.scatter
    PlotLines = pypl_axes_t.plot
    PlotText = pypl_axes_t.text
    PlotAnnotation = pypl_axes_t.annotate

    def SetTimeAxisProperties(self, latest: int, /) -> None:
        """"""
        self.set_xlim(0, latest)
        self.set_xticks(range(latest + 1))
        self.set_xticklabels(str(_idx) for _idx in range(latest + 1))

    def SetAxesPropertiesForTracking(self, tick_positions: Sequence[float], /) -> None:
        """"""
        self.set_xlabel("time points")
        self.set_ylabel("tracks")
        self.yaxis.set_label_position("right")
        self.yaxis.tick_right()
        self.yaxis.set_ticks(tick_positions)

    def PlotCellAnnotation(
        self, position: Tuple[float, float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_t, Sequence[annotation_t]]:
        """"""
        if isinstance(text, str):
            output = self.annotate(
                text,
                position,
                ha="center",
                **kwargs,
            )
        else:
            output = []

            renderer = self.figure.canvas.get_renderer()
            transform = self.transData
            for piece, properties in text:
                properties = {**properties, **kwargs}
                piece = self.text(*position, piece, transform=transform, **properties)
                piece.draw(renderer)
                extent = piece.get_window_extent()
                transform = trsf.offset_copy(
                    piece.get_transform(), x=extent.width, units="dots"
                )

                output.append(piece)

        return output

    def PlotImage(
        self, image: array_t, /, *, interval: Tuple[float, float] = None
    ) -> None:
        """"""
        pypl_image = self.matshow(image, cmap="gray")
        if interval is not None:
            pypl_image.set_clim(*interval)

        self.__image__ = pypl_image

    def UpdateImage(
        self,
        picture: array_t,
        /,
        *,
        interval: Tuple[float, float] = None,
        should_update_limits: bool = False,
    ) -> None:
        """"""
        self.__image__.set_array(picture)
        if should_update_limits:
            self.__image__.set_clim(*interval)


prjs.register_projection(axes_t)


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(figure_anyd_t):
    @classmethod
    def NewFigureAndAxes(
        cls, /, *, n_rows: int = 1, n_cols: int = 1, title: str = None
    ) -> Tuple[figure_t, Union[axes_t, Sequence[axes_t], Sequence[Sequence[axes_t]]],]:
        figure, axes = pypl.subplots(
            nrows=n_rows,
            ncols=n_cols,
            FigureClass=cls,
            subplot_kw={"projection": "ctBC_two_d_axes"},
        )

        if title is not None:
            first_axes = axes
            while isinstance(first_axes, Sequence):
                first_axes = first_axes[0]
            first_axes.set_title(title)

        return figure, axes


@dtcl.dataclass(repr=False, eq=False)
class s_viewer_2d_t(base_s_viewer_2d_t):
    def HighlightAnnotation(self, label: int, /, *, should_draw: bool = True) -> None:
        """"""
        if label == self.current_label:
            return

        for which, what in self.annotations:
            if not isinstance(what, Sequence):
                what = (what,)
            if label == which:
                color = CELL_ANNOTATION_COLOR_HIGHLIGHT
                bbox = CELL_ANNOTATION_BBOX_STYLE_HIGHLIGHT
            else:
                color = CELL_ANNOTATION_COLOR_DEFAULT
                bbox = CELL_ANNOTATION_BBOX_STYLE_DEFAULT
            for text in what:
                text.set_color(color)
                if "\n" in text.get_text():
                    text.set_bbox(bbox)

        self.current_label = label

        if should_draw:
            self.figure.canvas.draw_idle()

    def AddColorbarForImage(self) -> None:
        """"""
        self.figure.colorbar(self.axes.__image__, ax=self.axes)

    def _ActivateEventProcessing(self, more_than_one: bool, /) -> None:
        """"""
        SetMatplotlibConfig("keymap", save=[])
        super()._ActivateEventProcessing(more_than_one)


@dtcl.dataclass(repr=False, eq=False)
class t_viewer_2d_t(base_t_viewer_2d_t):
    def _ShowAnnotation(
        self,
        event: mouse_event_t,
        /,
    ) -> None:
        """"""
        inside, details = self.scatter.contains(event)
        if inside:
            idx = details["ind"][0]
            time_point = self.time_points[idx]
            label = self.labels[idx]

            position = self.scatter.get_offsets()[idx]
            text = f"Time {time_point}\nCell {label}\nAffty {self.affinities[idx]:.2f}"
            self.annotation.xy = position
            self.annotation.set_text(text)
            self.annotation.set_visible(True)

            self.viewer.ShowFrame(time_point=time_point, highlighted=label)
