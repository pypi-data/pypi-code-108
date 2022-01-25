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
from typing import Any, Callable, Sequence, Tuple, Union

import matplotlib.pyplot as pypl
import numpy as nmpy
from matplotlib import cm as colormap_t
from matplotlib.backend_bases import Event as event_t
from matplotlib.colors import LinearSegmentedColormap as linear_colormap_t
from matplotlib.lines import Line2D as line_t
from matplotlib.text import Annotation as annotation_t
from matplotlib.widgets import Slider as slider_t

from cell_tracking_BC.in_out.file.archiver import archiver_t
from cell_tracking_BC.in_out.graphics.context import axes_t as base_axes_t
from cell_tracking_BC.in_out.graphics.context import figure_t as base_figure_t
from cell_tracking_BC.in_out.text.logger import LOGGER, WhereMethod


array_t = nmpy.ndarray
pypl_axes_t = pypl.Axes
pypl_figure_t = pypl.Figure


_SHOWN_FIGURES = []


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_t(pypl_axes_t, base_axes_t):
    def SetTitle(self, title: str, /) -> None:
        """"""
        if self.axison:
            self.set_title(title)

    def SetYAxisTicks(
        self, positions: Sequence[float], labels: Sequence[str], /
    ) -> None:
        """"""
        self.yaxis.set_ticks(positions)
        self.yaxis.set_ticklabels(labels)

    def TurnTicksOff(
        self,
    ) -> None:
        """"""
        self.set_axis_off()

    def Freeze(self) -> None:
        """"""
        self.autoscale(enable=False)

    def ShowLegend(self) -> None:
        """"""
        self.legend()

    def AddStandardColormap(
        self, name: str, colormap: str, /, *, position: str = "right"
    ) -> colormap_t:
        """"""
        output = colormap_t.get_cmap(colormap)

        _AddColorbar(name, self.figure, self, output, position=position)

        return output

    def AddColormapFromMilestones(
        self,
        name: str,
        milestones: Sequence[Tuple[float, str]],
        /,
        *,
        position: str = "right",
    ) -> colormap_t:
        """"""
        output = linear_colormap_t.from_list(name, milestones)

        _AddColorbar(name, self.figure, self, output, position=position)

        return output

    def RemoveLinesAndAnnotations(self) -> None:
        """"""
        to_be_removed = filter(
            lambda _art: isinstance(_art, (annotation_t, line_t)),
            self.get_children(),
        )

        # tuple: to build a static list before iterative removal, just in case
        for annotation in tuple(to_be_removed):
            annotation.remove()

    def Figure(self) -> figure_t:
        """"""
        return self.figure


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(pypl_figure_t, base_figure_t):

    ActivateTightLayout = pypl_figure_t.tight_layout

    def Show(
        self,
        /,
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        """
        in_main_thread: disregarded
        """
        if self in _SHOWN_FIGURES:
            return

        self.show()
        _SHOWN_FIGURES.append(self)

        event_manager = self.canvas
        if interactively:
            if in_main_thread:
                event_manager.mpl_connect(
                    "close_event", lambda _: _StopEventLoop(event_manager, self)
                )
                event_manager.start_event_loop()
            else:
                LOGGER.warn(
                    f"{WhereMethod(self, self.Show)}: Interactivity is not possible outside the main thread"
                )
                # There seems to be no solution to have interactivity out of the main thread with Matplotlib
                event_manager.mpl_connect(
                    "close_event", lambda _: _SHOWN_FIGURES.remove(self)
                )
        else:
            event_manager.mpl_connect(
                "close_event", lambda _: _SHOWN_FIGURES.remove(self)
            )

    @staticmethod
    def ShowAll(
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        """"""
        if in_main_thread:
            pypl.show(block=interactively)
        else:
            for number in pypl.get_fignums():
                figure = pypl.figure(number)
                # Remember that in_main_thread is False
                figure.Show(interactively=interactively, in_main_thread=False)

    def Update(self, /, *, gently: bool = True) -> None:
        """"""
        if gently:
            self.canvas.draw_idle()
        else:
            self.canvas.draw()

    def Content(self, /) -> array_t:
        """
        Alternative:
            - fig.canvas.renderer._renderer?
            - Agg Buffer To Array: np.array(canvas.renderer.buffer_rgba())
        """
        height, width = self.canvas.get_width_height()
        output = nmpy.fromstring(self.canvas.tostring_rgb(), dtype=nmpy.uint8)
        output.shape = (width, height, 3)

        return output

    def Save(self, path: Union[str, path_t], /) -> None:
        """"""
        self.savefig(path, dpi=300)

    def Archive(
        self,
        /,
        *,
        name: str = "figure",
        archiver: archiver_t = None,
    ) -> None:
        """"""
        if archiver is not None:
            self.canvas.draw_idle()
            archiver.Store(self, name)

    def ActivateEvent(self, event: str, processor: Callable[[event_t], Any], /) -> None:
        """"""
        self.canvas.mpl_connect(event, processor)

    def Close(self, /) -> None:
        """"""
        pypl.close(fig=self)


def _StopEventLoop(event_manager: pypl.FigureCanvasBase, figure: figure_t, /) -> None:
    """"""
    event_manager.stop_event_loop()
    _SHOWN_FIGURES.remove(figure)


def _AddColorbar(
    name: str,
    figure: figure_t,
    axes: axes_t,
    colormap: colormap_t,
    /,
    *,
    position: str = "right",
) -> None:
    """"""
    mappable = colormap_t.ScalarMappable(cmap=colormap)
    figure.colorbar(mappable, ax=axes, location=position, label=name)


def NewSlider(figure: figure_t, n_steps: int, /) -> slider_t:
    """"""
    slider_axes = figure.add_axes([0.15, 0.04, 0.7, 0.03])

    return slider_t(
        slider_axes,
        "Time Point",
        0,
        n_steps - 1,
        valinit=0,
        valstep=1,
    )


def SliderValue(slider: slider_t, /) -> float:
    """"""
    return slider.val


def UpdateSlider(slider: slider_t, value: float, /) -> None:
    """"""
    slider.set_val(value)
