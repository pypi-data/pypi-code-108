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

from typing import Optional

import numpy as nmpy

import cell_tracking_BC.in_out.graphics.generic.three_d as thrd
from cell_tracking_BC.in_out.file.archiver import archiver_t
from cell_tracking_BC.in_out.graphics.context import axes_3d_t, context_t, figure_t
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.context import DRAWING_CONTEXT
from cell_tracking_BC.type.sequence import sequence_t
from cell_tracking_BC.type.track import unstructured_track_t


_LOW_AFFINITY = 0.75
_MATPLOTLIB_COLORS = ("b", "g", "r", "c", "m", "y", "k")


def ShowTracking2D(
    sequence: sequence_t,
    /,
    *,
    version: str = None,
    with_segmentation: bool = True,
    with_cell_labels: bool = True,
    with_track_labels: bool = True,
    with_ticks: bool = True,
    with_colorbar: bool = True,
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    figure_name: str = "tracking 2D",
    dbe: context_t = DRAWING_CONTEXT,
    archiver: archiver_t = None,
) -> Optional[figure_t]:
    """"""
    output = None

    viewer = dbe.t_viewer_2d_t.NewForSequence(
        sequence,
        dbe,
        version=version,
        with_segmentation=with_segmentation,
        with_cell_labels=with_cell_labels,
        with_track_labels=with_track_labels,
        with_ticks=with_ticks,
        with_colorbar=with_colorbar,
        figure_name=figure_name,
        archiver=archiver,
    )

    if prepare_only:
        output = viewer
    else:
        viewer.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output


def ShowTracking3D(
    sequence: sequence_t,
    /,
    *,
    with_track_labels: bool = True,
    with_cell_labels: bool = True,
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[figure_t]:
    """"""
    output = None

    figure, axes = dbe.figure_3d_t.NewFigureAndAxes()
    axes: axes_3d_t
    colormap = axes.AddColormapFromMilestones(
        "Tracking Affinity", ((0.0, "black"), (0.75, "red"), (1.0, "blue"))
    )

    thrd.ShowFirstFrameAsFloor(sequence.cell_frames[0], axes)

    time_scaling = axes.__class__.TimeScaling(sequence.shape, sequence.length)
    for t_idx, track in enumerate(sequence.tracks):
        low_affinities = tuple(_ffn < _LOW_AFFINITY for _ffn in track.affinities)
        low_fraction = nmpy.count_nonzero(low_affinities) / (
            0.3 * low_affinities.__len__()
        )
        color = colormap(1.0 - min(1.0, low_fraction))

        for piece in track.Pieces():
            rows, cols, times, *labels = piece.AsRowsColsTimes(
                with_labels=with_cell_labels
            )
            times = tuple(time_scaling * _tme for _tme in times)

            axes.PlotLines(rows, cols, times, color=color)

            if with_cell_labels:
                for row, col, time, label in zip(rows, cols, times, labels[0]):
                    axes.PlotText(
                        row,
                        col,
                        time,
                        str(label),
                        fontsize="x-small",
                        color=color,
                    )
            if with_track_labels and (piece.label is not None):
                axes.PlotText(
                    rows[-1],
                    cols[-1],
                    times[-1] + 0.25,
                    str(piece.label),
                    fontsize="x-small",
                    color=color,
                )

    axes.SetTimeAxisProperties(sequence.length - 1)

    if prepare_only:
        output = figure
    else:
        figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output


def ShowUnstructuredTracking3D(
    sequence: sequence_t,
    /,
    *,
    with_cell_labels: bool = True,
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[figure_t]:
    """"""
    output = None

    invalids = sequence.tracks.invalids[unstructured_track_t]
    if (invalids is None) or (invalids.__len__() == 0):
        return

    figure, axes = dbe.figure_3d_t.NewFigureAndAxes()
    axes: axes_3d_t

    colors = _MATPLOTLIB_COLORS
    for t_idx, (track, _) in enumerate(invalids):
        color_idx = t_idx % colors.__len__()

        for time_point, *cells, _ in track.segments_iterator:
            rows, cols = tuple(zip(*(_cll.centroid.tolist() for _cll in cells)))
            times = (time_point, time_point + 1)

            axes.PlotLines(rows, cols, times, colors[color_idx])

            if with_cell_labels:
                labels = tuple(_cll.label for _cll in cells)
                for row, col, time, label in zip(rows, cols, times, labels[0]):
                    axes.PlotText(
                        row,
                        col,
                        time,
                        str(label),
                        fontsize="x-small",
                        color=colors[color_idx],
                    )

    axes.SetTimeAxisProperties(sequence.length - 1)

    if prepare_only:
        output = figure
    else:
        figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output
