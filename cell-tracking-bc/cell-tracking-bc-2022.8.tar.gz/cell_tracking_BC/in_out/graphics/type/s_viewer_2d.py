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
import datetime as dttm
import re as regx
from pathlib import Path as path_t
from typing import Callable, Dict, Sequence, Tuple, Union

import numpy as nmpy
import tifffile as tiff

from cell_tracking_BC.in_out.graphics.type.axes import axes_2d_t as axes_t
from cell_tracking_BC.in_out.graphics.type.context import context_t
from cell_tracking_BC.in_out.graphics.type.event import (
    event_h,
    event_key_h,
    event_scroll_h,
)
from cell_tracking_BC.in_out.graphics.type.s_drawer_2d import (
    s_drawer_2d_t,
    AllChannelsOfSequence,
)
from cell_tracking_BC.type.frame import frame_t
from cell_tracking_BC.type.sequence import BoundingBoxSlices, sequence_h


array_t = nmpy.ndarray

all_versions_h = Dict[
    str, Tuple[Tuple[int, int], Union[Sequence[array_t], Sequence[frame_t]]]
]


@dtcl.dataclass(repr=False, eq=False)
class s_viewer_2d_t(s_drawer_2d_t):
    @classmethod
    def _NewForSequence(
        cls,
        sequence: sequence_h,
        AllVersionsOfSequence: Callable[[sequence_h], Tuple[all_versions_h, str]],
        dbe: context_t,
        /,
        *,
        version: str = None,
        with_segmentation: bool = False,
        with_cell_labels: bool = True,
        cell_frames: Sequence[frame_t] = None,
        with_track_labels: bool = True,
        in_axes: axes_t = None,
        with_ticks: bool = True,
    ) -> s_viewer_2d_t:
        """"""
        drawer = s_drawer_2d_t._NewForSequence(
            sequence,
            AllVersionsOfSequence,
            dbe,
            version=version,
            with_segmentation=with_segmentation,
            with_cell_labels=with_cell_labels,
            cell_frames=cell_frames,
            with_track_labels=with_track_labels,
            in_axes=in_axes,
            with_ticks=with_ticks,
        )
        if in_axes is None:
            current_time_point = None
            slider = dbe.NewSlider(drawer.figure, sequence.length)
        else:
            current_time_point = 0
            slider = None

        arguments = {
            "figure": drawer.figure,
            "axes": drawer.axes,
            "all_versions": drawer.all_versions,
            "current_time_point": current_time_point,
            "slider": slider,
        }
        instance = cls(**arguments)
        already_set = tuple(arguments.keys())
        for field in dtcl.fields(drawer):
            if (name := field.name) not in already_set:
                setattr(instance, name, getattr(drawer, name))

        instance._ActivateEventProcessing(instance.all_versions.__len__() > 1)

        return instance

    def _ActivateEventProcessing(self, more_than_one_version: bool, /) -> None:
        """"""
        self.figure.ActivateEvent("key_press_event", self._OnKeyPress)
        if more_than_one_version:
            self.figure.ActivateEvent("button_press_event", self._OnButtonPress)
        if self.slider is not None:
            self.figure.ActivateEvent("scroll_event", self._OnScrollEvent)

    def ShowNextVersion(self, /, *, should_draw: bool = True) -> None:
        """"""
        all_names = tuple(self.all_versions.keys())
        where = all_names.index(self.current_version)
        where = (where + 1) % all_names.__len__()
        new_version = all_names[where]

        self.ShowFrame(
            version=new_version, should_update_limits=True, should_draw=should_draw
        )

    def Show(
        self,
        /,
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        """"""
        self.figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    def _OnKeyPress(
        self,
        event: event_key_h,
        /,
    ) -> None:
        """"""
        if self.dbe.KeyEventKey(event).lower() == "s":
            print("Sequence saving in progress...")
            volume = self.AsAnnotatedVolume()

            illegal = "[^-_a-zA-Z0-9]"
            version = regx.sub(illegal, "", self.current_version)
            now = regx.sub(illegal, "-", dttm.datetime.now().isoformat())
            path = path_t.home() / f"sequence-{version}-{now}.tif"
            if path.exists():
                print(f"{path}: Existing path; Cannot override")
                return

            tiff.imwrite(
                str(path),
                volume,
                photometric="rgb",
                compression="deflate",
                planarconfig="separate",
                metadata={"axes": "XYZCT"},
            )
            print(f"Annotated sequence saved at: {path}")

    def _OnButtonPress(
        self,
        event: event_h,
        /,
    ) -> None:
        """"""
        if self.dbe.IsTargetOfEvent(self.axes, event):
            self.ShowNextVersion()
        elif (self.slider is not None) and self.dbe.IsTargetOfEvent(
            self.dbe.SliderAxes(self.slider), event
        ):
            self.ShowFrame(
                time_point=self.dbe.SliderValue(self.slider), force_update=True
            )

    def _OnScrollEvent(self, event: event_scroll_h) -> None:
        """"""
        value = self.dbe.SliderValue(self.slider)
        bounds = self.dbe.SliderBounds(self.slider)
        new_value = round(value + nmpy.sign(self.dbe.ScrollEventStep(event)))
        new_value = min(max(new_value, bounds[0]), bounds[1])
        if new_value != value:
            self.ShowFrame(time_point=new_value)

    def AsAnnotatedVolume(self) -> array_t:
        """
        See: cell_tracking_BC.in_out.file.sequence.SaveAnnotatedSequence
        """
        # Cannot be initialized since content (not frame) shape is unknown
        output = None

        current_version = self.all_versions[self.current_version][1]
        sequence_length = current_version.__len__()

        figure, axes = self.dbe.figure_2d_t.NewFigureAndAxes()
        axes: axes_t
        invisible = self.__class__._NewForSequence(
            current_version,
            AllChannelsOfSequence,
            self.dbe,
            with_cell_labels=self.with_cell_labels,
            cell_frames=self.cell_frames,
            with_track_labels=False,
            with_ticks=False,
            in_axes=axes,
        )
        invisible.cell_contours = self.cell_contours
        invisible.tracks = self.tracks

        for time_point in range(sequence_length):
            invisible.ShowFrame(time_point=time_point, should_draw=False)
            # draw_idle is not appropriate here
            figure.Update(gently=False)
            content = figure.Content()
            if output is None:
                output = nmpy.empty((*content.shape, sequence_length), dtype=nmpy.uint8)
            output[..., time_point] = content

        figure.Close()  # To prevent remaining caught in event loop

        row_slice, col_slice = BoundingBoxSlices(output)
        output = output[row_slice, col_slice, :, :]
        output = nmpy.moveaxis(output, (0, 1, 2, 3), (2, 3, 1, 0))
        output = output[:, nmpy.newaxis, :, :, :]

        return output
