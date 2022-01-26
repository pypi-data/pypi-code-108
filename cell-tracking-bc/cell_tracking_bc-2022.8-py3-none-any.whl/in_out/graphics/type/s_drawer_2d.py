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
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as nmpy

import cell_tracking_BC.in_out.graphics.generic.d_any as gphc
from cell_tracking_BC.in_out.graphics.type.annotation import annotation_h
from cell_tracking_BC.in_out.graphics.type.axes import axes_2d_t as axes_t
from cell_tracking_BC.in_out.graphics.type.context import context_t
from cell_tracking_BC.in_out.graphics.type.figure import figure_t
from cell_tracking_BC.in_out.graphics.type.signatures import signatures_p
from cell_tracking_BC.in_out.graphics.type.widget import slider_h
from cell_tracking_BC.type.frame import frame_t
from cell_tracking_BC.type.segmentation import compartment_t, segmentation_t
from cell_tracking_BC.type.segmentations import segmentations_t
from cell_tracking_BC.type.sequence import sequence_h, sequence_t
from cell_tracking_BC.type.tracks import tracks_t


array_t = nmpy.ndarray

all_versions_h = Dict[
    str, Tuple[Tuple[int, int], Union[Sequence[array_t], Sequence[frame_t]]]
]


@dtcl.dataclass(repr=False, eq=False)
class s_drawer_2d_t:

    figure: figure_t
    axes: axes_t

    all_versions: all_versions_h
    current_version: str = None
    current_time_point: int = -1  # Used only when slider is None
    current_label: int = -1

    slider: slider_h = None

    # Only meaningful for NewForChannels
    cell_contours: Sequence[Sequence[array_t]] = None
    # Using frame labeling for array_t's, or cell_frames below for sequence_t
    with_cell_labels: bool = False
    cell_frames: Sequence[frame_t] = None
    tracks: tracks_t = None
    annotations: Sequence[
        Tuple[int, Union[annotation_h, Sequence[annotation_h]]]
    ] = None

    dbe: context_t = None

    @classmethod
    def NewForChannels(
        cls,
        sequence: Union[Sequence[array_t], sequence_t],
        dbe: context_t,
        /,
        *,
        channel: str = None,
        with_segmentation: bool = False,
        with_cell_labels: bool = False,
        with_track_labels: bool = False,
        in_axes: axes_t = None,
        with_ticks: bool = True,
        with_colorbar: bool = True,
    ) -> s_drawer_2d_t:
        """"""
        with_cell_labels = (
            with_cell_labels and isinstance(sequence, sequence_t) and sequence.has_cells
        )
        if isinstance(sequence, sequence_t) and sequence.has_cells:
            cell_frames = sequence.cell_frames
        else:
            cell_frames = None

        instance = cls._NewForSequence(
            sequence,
            AllChannelsOfSequence,
            dbe,
            version=channel,
            with_segmentation=with_segmentation,
            with_cell_labels=with_cell_labels,
            cell_frames=cell_frames,
            with_track_labels=with_track_labels,
            in_axes=in_axes,
            with_ticks=with_ticks,
        )
        if with_colorbar:
            instance.AddColorbarForImage()

        return instance

    @classmethod
    def NewForSegmentation(
        cls,
        sequence: sequence_h,
        dbe: context_t,
        /,
        *,
        version: str = None,
        with_cell_labels: bool = True,
        with_track_labels: bool = True,
        in_axes: axes_t = None,
        with_ticks: bool = True,
    ) -> s_drawer_2d_t:
        """"""
        if (
            isinstance(sequence, Sequence)
            and isinstance(sequence[0], segmentation_t)
            and not isinstance(sequence, segmentations_t)
        ):
            new_sequence = segmentations_t()
            for segmentation in sequence:
                new_sequence.append(segmentation)
            sequence = new_sequence

        if isinstance(sequence, sequence_t) and sequence.has_cells:
            cell_frames = sequence.cell_frames
        else:
            cell_frames = None

        return cls._NewForSequence(
            sequence,
            _AllSegmentationsOfSequence,
            dbe,
            version=version,
            with_cell_labels=with_cell_labels,
            cell_frames=cell_frames,
            with_track_labels=with_track_labels,
            in_axes=in_axes,
            with_ticks=with_ticks,
        )

    @classmethod
    def NewForAllStreams(
        cls,
        sequence: sequence_t,
        dbe: context_t,
        /,
        *,
        version: str = None,
        with_segmentation: bool = False,
        with_cell_labels: bool = False,
        with_track_labels: bool = False,
        in_axes: axes_t = None,
        with_ticks: bool = True,
        with_colorbar: bool = True,
    ) -> s_drawer_2d_t:
        """"""
        with_cell_labels = with_cell_labels and sequence.has_cells
        if sequence.has_cells:
            cell_frames = sequence.cell_frames
        else:
            cell_frames = None

        instance = cls._NewForSequence(
            sequence,
            _AllStreamsOfSequence,
            dbe,
            version=version,
            with_segmentation=with_segmentation,
            with_cell_labels=with_cell_labels,
            cell_frames=cell_frames,
            with_track_labels=with_track_labels,
            in_axes=in_axes,
            with_ticks=with_ticks,
        )
        if with_colorbar:
            instance.AddColorbarForImage()

        return instance

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
    ) -> s_drawer_2d_t:
        """"""
        if in_axes is None:
            figure, axes = dbe.figure_2d_t.NewFigureAndAxes()
        else:
            figure = in_axes.Figure()
            axes = in_axes
        if not with_ticks:
            axes.TurnTicksOff()

        all_versions, current_version = AllVersionsOfSequence(sequence)
        if version is not None:
            current_version = version
        if all_versions.__len__() > 1:
            axes.SetTitle(current_version)

        cell_contours = gphc.CellContours(sequence, with_segmentation)
        tracks = gphc.CellTracks(sequence, with_track_labels)

        cell_annotations = _ShowFirstFrame(
            all_versions,
            current_version,
            cell_contours,
            with_cell_labels,
            cell_frames,
            tracks,
            axes,
            dbe.CellAnnotationStyle,
        )

        instance = cls(
            figure=figure,
            axes=axes,
            all_versions=all_versions,
            current_version=current_version,
            current_time_point=0,
            cell_contours=cell_contours,
            with_cell_labels=with_cell_labels,
            tracks=tracks,
            cell_frames=cell_frames,
            annotations=cell_annotations,
            dbe=dbe,
        )

        return instance

    def AddColorbarForImage(self) -> None:
        """"""
        raise NotImplementedError

    def ShowFrame(
        self,
        /,
        *,
        version: str = None,
        time_point: Union[int, float] = None,
        highlighted: int = -1,
        should_update_limits: bool = False,
        should_draw: bool = True,
        force_update: bool = False,
    ) -> None:
        """
        force_update: If the slider has been updated externally, the time point will not be considered new, and no
        update will be made. Hence, this parameter.
        """
        if version is None:
            version = self.current_version
        if self.slider is None:
            current_time_point = self.current_time_point
        else:
            current_time_point = self.slider.val
        if time_point is None:
            time_point = current_time_point
        else:
            time_point = int(time_point)

        version_is_new = version != self.current_version
        time_point_is_new = (time_point != current_time_point) or force_update

        if version_is_new or time_point_is_new:
            interval, frames = self.all_versions[version]
            frame = frames[time_point]
            self.axes.UpdateImage(
                frame, interval=interval, should_update_limits=should_update_limits
            )
        else:
            frame = None

        if self.annotations is not None:
            if time_point_is_new:
                if self.cell_contours is None:
                    contours = None
                else:
                    contours = self.cell_contours[time_point]
                if self.cell_frames is None:
                    cell_frame = None
                else:
                    cell_frame = self.cell_frames[time_point]

                self.annotations = self.axes.PlotCellsDetails(
                    frame,
                    contours,
                    self.with_cell_labels,
                    cell_frame,
                    self.tracks,
                    self.dbe.CellAnnotationStyle,
                    highlighted=highlighted,
                )
                self.current_label = highlighted
            elif highlighted > 0:
                self.HighlightAnnotation(highlighted, should_draw=False)

        if version_is_new:
            self.axes.SetTitle(version)
            self.current_version = version

        if time_point_is_new:
            if self.slider is None:
                self.current_time_point = time_point
            else:
                self.dbe.UpdateSlider(self.slider, time_point)

        if should_draw:
            self.figure.Update()

    def HighlightAnnotation(self, label: int, /, *, should_draw: bool = True) -> None:
        """
        If label is <= 0 or > max cell label in current frame, then un-highlights all annotations
        """
        raise NotImplementedError


def AllChannelsOfSequence(
    sequence: Union[Sequence[array_t], sequence_t]
) -> Tuple[all_versions_h, str]:
    """"""
    if isinstance(sequence, sequence_t):
        all_channels = {}
        for channel in sequence.channels:
            frames = sequence.Frames(channel=channel)
            min_value = min(nmpy.amin(_frm) for _frm in frames)
            max_value = max(nmpy.amax(_frm) for _frm in frames)
            all_channels[channel] = ((min_value, max_value), frames)
        current_channel = sequence.channels[0]
    else:
        current_channel = "MAIN"
        min_value = min(nmpy.amin(_frm) for _frm in sequence)
        max_value = max(nmpy.amax(_frm) for _frm in sequence)
        all_channels = {current_channel: ((min_value, max_value), sequence)}

    return all_channels, current_channel


def _AllSegmentationsOfSequence(sequence: sequence_h) -> Tuple[all_versions_h, str]:
    """"""
    if isinstance(sequence, (segmentations_t, sequence_t)):
        if isinstance(sequence, segmentations_t):
            segmentations = sequence
        else:
            segmentations = sequence.segmentations

        all_versions = {}
        compartments, versions = segmentations.available_versions
        for compartment in compartments:
            for version in versions:
                key = f"{compartment.name}:{version[0]}:{version[1]}"
                frames = segmentations.CompartmentsWithVersion(
                    compartment, index=version[0], name=version[1]
                )
                all_versions[key] = ((0, 1), frames)
        current_version = f"{compartment_t.CELL.name}:{versions[0][0]}:{versions[0][1]}"
    else:
        current_version = "MAIN"
        all_versions = {current_version: ((0, 1), sequence)}

    return all_versions, current_version


def _AllStreamsOfSequence(sequence: sequence_t) -> Tuple[all_versions_h, str]:
    """"""
    all_streams, current_stream = AllChannelsOfSequence(sequence)
    all_versions, _ = _AllSegmentationsOfSequence(sequence)

    all_streams.update(all_versions)

    return all_streams, current_stream


def _ShowFirstFrame(
    all_versions: all_versions_h,
    current_version: str,
    cell_contours: Optional[Sequence[Sequence[array_t]]],
    with_cell_labels: bool,
    cell_frames: Optional[Sequence[frame_t]],
    tracks: Optional[tracks_t],
    axes: axes_t,
    CellAnnotationStyle: signatures_p.cell_annotation_style_h,
    /,
) -> Optional[Sequence[Tuple[int, annotation_h]]]:
    """"""
    interval, version = all_versions[current_version]
    first_frame = version[0]

    axes.PlotImage(first_frame, interval=interval)

    if (cell_contours is not None) or with_cell_labels or (tracks is not None):
        if cell_contours is None:
            contours = None
        else:
            contours = cell_contours[0]
        if cell_frames is None:
            cell_frame = None
        else:
            cell_frame = cell_frames[0]
        cell_annotations = axes.PlotCellsDetails(
            first_frame,
            contours,
            with_cell_labels,
            cell_frame,
            tracks,
            CellAnnotationStyle,
        )
    else:
        cell_annotations = None

    # Once the first frame has been plot, disable axes autoscale to try to speed future plots up
    axes.Freeze()

    return cell_annotations
