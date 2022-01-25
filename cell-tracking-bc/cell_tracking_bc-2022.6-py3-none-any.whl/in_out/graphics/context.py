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
from pathlib import Path as path_t
from typing import Any, Callable, Dict
from typing import NamedTuple as named_tuple_t
from typing import Protocol, Sequence, Tuple, Type, TypeVar, Union

from numpy import ndarray as array_t

from cell_tracking_BC.in_out.file.archiver import archiver_t


annotation_h = TypeVar("annotation_h")
element_h = TypeVar("element_h")
event_h = TypeVar("event_h")
frame_h = TypeVar("frame_h")
key_event_h = TypeVar("key_event_h")
path_collection_h = TypeVar("path_collection_h")
s_viewer_2d_h = TypeVar("s_viewer_2d_h")
scroll_event_h = TypeVar("scroll_event_h")
slider_h = TypeVar("slider_h")
t_viewer_2d_h = TypeVar("t_viewer_2d_h")

# "some_text" or (("text1", properties1), ("text2", properties2)...)
cell_annotation_h = Union[str, Sequence[Tuple[str, Dict[str, Any]]]]
rgb_color_h = Tuple[float, float, float]
rgba_color_h = Tuple[float, float, float, float]
colormap_h = Callable[
    [Union[float, Sequence[float]]], Union[rgba_color_h, Sequence[rgba_color_h]]
]


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_t:
    def SetTitle(self, title: str, /) -> None:
        pass

    def SetYAxisTicks(
        self, positions: Sequence[float], labels: Sequence[str], /
    ) -> None:
        pass

    def SetTimeAxisProperties(self, latest: int, /) -> None:
        pass

    def TurnTicksOff(self) -> None:
        pass

    def Freeze(self) -> None:
        pass

    def ShowLegend(self) -> None:
        pass

    # def RemoveArtists(self, which: Union[type, Sequence[type]], /) -> None:
    #     pass

    def AddStandardColormap(
        self, name: str, colormap: str, /, *, position: str = "right"
    ) -> colormap_h:
        pass

    def AddColormapFromMilestones(
        self,
        name: str,
        milestones: Sequence[Tuple[float, str]],
        /,
        *,
        position: str = "right",
    ) -> colormap_h:
        pass

    def RemoveLinesAndAnnotations(self) -> None:
        pass

    def Figure(self) -> figure_t:
        pass


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_2d_t(axes_t):
    def SetAxesPropertiesForTracking(self, tick_positions: Sequence[float], /) -> None:
        pass

    def PlotPoints(
        self,
        x,
        y,
        s=None,
        c=None,
        marker=None,
        cmap=None,
        norm=None,
        vmin=None,
        vmax=None,
        alpha=None,
        linewidths=None,
        *,
        edgecolors=None,
        plotnonfinite=False,
        data=None,
        **kwargs,
    ):
        pass

    def PlotLines(self, *args, scalex=True, scaley=True, data=None, **kwargs):
        pass

    def PlotText(self, x, y, s, fontdict=None, **kwargs):
        pass

    def PlotAnnotation(self, text, xy, *args, **kwargs):
        pass

    def PlotCellAnnotation(
        self, position: Tuple[float, float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_h, Sequence[annotation_h]]:
        pass

    def PlotImage(
        self, image: array_t, /, *, interval: Tuple[float, float] = None
    ) -> None:
        """"""
        pass

    def UpdateImage(
        self,
        picture: array_t,
        /,
        *,
        interval: Tuple[float, float] = None,
        should_update_limits: bool = False,
    ) -> None:
        """"""
        pass


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_3d_t(axes_t):
    @staticmethod
    def TimeScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        return 1.0

    @staticmethod
    def MillefeuilleScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        return 1.0

    def PlotPoints(
        self, xs, ys, zs=0, zdir="z", s=20, c=None, depthshade=True, *args, **kwargs
    ):
        pass

    def PlotLines(self, xs, ys, *args, zdir="z", **kwargs):
        pass

    def PlotText(self, x, y, z, s, zdir=None, **kwargs):
        pass

    def PlotAnnotation(self, text, xyz, *args, **kwargs):
        pass

    def PlotCellAnnotation(
        self, position: Tuple[float, float, float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_h, Sequence[annotation_h]]:
        pass

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
        pass

    def PlotIsosurface(
        self,
        volume: array_t,
        iso_value: float,
        /,
        should_be_capped: bool = False,
        keep_every: int = 2,
        **kwargs,
    ) -> None:
        pass


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t:
    @classmethod
    def NewFigureAndAxes(
        cls, /, *, n_rows: int = 1, n_cols: int = 1, title: str = None
    ) -> Tuple[figure_t, Union[axes_t, Sequence[axes_t], Sequence[Sequence[axes_t]]]]:
        pass

    def ActivateTightLayout(self, *, pad=1.08, h_pad=None, w_pad=None, rect=None):
        pass

    def Show(
        self,
        /,
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        pass

    @staticmethod
    def ShowAll(
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        pass

    def Update(self, /, *, gently: bool = True) -> None:
        pass

    def Content(self, /) -> array_t:
        pass

    def Save(self, path: Union[str, path_t], /) -> None:
        pass

    def Archive(
        self,
        /,
        *,
        name: str = "figure",
        archiver: archiver_t = None,
    ) -> None:
        pass

    def ActivateEvent(self, event: str, processor: Callable[[event_h], Any], /) -> None:
        pass

    def Close(self) -> None:
        pass


class _sg(Protocol):  # sg=signature
    @staticmethod
    def cell_annotation_style_h(
        highlighted: bool, multi_track: bool, /
    ) -> Dict[str, Any]:
        ...

    @staticmethod
    def new_slider_h(figure: figure_t, n_steps: int, /) -> slider_h:
        ...

    @staticmethod
    def slider_value_h(slider: slider_h, /) -> float:
        ...

    @staticmethod
    def update_slider_h(slider: slider_h, value: float, /) -> None:
        ...

    @staticmethod
    def slider_bounds_h(slider: slider_h, /) -> Sequence[float]:
        ...

    @staticmethod
    def slider_axes_h(slider: slider_h, /) -> axes_2d_t:
        ...

    @staticmethod
    def get_visibility_h(what: element_h, /) -> bool:
        ...

    @staticmethod
    def set_visibility_h(what: element_h, visibility: bool, /) -> None:
        ...

    @staticmethod
    def is_target_of_event_h(axes: axes_t, event: event_h, /) -> bool:
        ...

    @staticmethod
    def key_event_key_h(event: key_event_h, /) -> str:
        ...

    @staticmethod
    def scroll_event_step_h(event: scroll_event_h, /) -> float:
        ...


class context_t(named_tuple_t):
    figure_2d_t: Type[figure_t] = None
    figure_3d_t: Type[figure_t] = None
    axes_2d_t: Type[axes_2d_t] = None
    axes_3d_t: Type[axes_3d_t] = None
    s_viewer_2d_t: s_viewer_2d_h = None
    t_viewer_2d_t: t_viewer_2d_h = None
    CellAnnotationStyle: _sg.cell_annotation_style_h = lambda: {}
    NewSlider: _sg.new_slider_h = None
    SliderValue: _sg.slider_value_h = None
    UpdateSlider: _sg.update_slider_h = None
    SliderBounds: _sg.slider_bounds_h = None
    SliderAxes: _sg.slider_axes_h = lambda: None
    IsVisible: _sg.get_visibility_h = None
    SetVisibility: _sg.set_visibility_h = None
    IsTargetOfEvent: _sg.is_target_of_event_h = lambda: True
    KeyEventKey: _sg.key_event_key_h = None
    ScrollEventStep: _sg.scroll_event_step_h = None
