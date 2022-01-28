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

from typing import Callable, Optional, Tuple, Type, Union

import matplotlib.pyplot as pypl
import numpy as nmpy

from cell_tracking_BC.in_out.graphics.dbe.matplotlib.d_2 import (
    figure_t as figure_2d_t,
    s_drawer_2d_t,
)
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.context import DRAWING_CONTEXT
from cell_tracking_BC.in_out.graphics.type.axes import axes_2d_t
from cell_tracking_BC.in_out.graphics.type.context import context_t
from cell_tracking_BC.in_out.graphics.type.figure import figure_t
from cell_tracking_BC.in_out.graphics.type.s_drawer_2d import (
    s_drawer_2d_t as s_drawer_t,
)
from cell_tracking_BC.type.sequence import sequence_h, sequence_t


array_t = nmpy.ndarray


def AsAnnotatedVolume(
    sequence: sequence_h,
    channel: str,
    with_segmentation: bool,
    with_cell_labels: bool,
    with_track_labels: bool,
    /,
    *,
    drawer: Union[s_drawer_t, s_drawer_2d_t] = None,
    SaveFrame: Callable[[array_t, int], None] = None,
) -> Optional[array_t]:
    """"""
    output = None  # Cannot be initialized since content (not frame) shape is unknown

    if drawer is None:
        figure, axes, drawer = FigureAxesAndDrawer(
            figure_2d_t,
            s_drawer_2d_t,
            sequence,
            channel,
            with_segmentation,
            with_cell_labels,
            with_track_labels,
            DRAWING_CONTEXT,
            True,
        )
    else:
        figure, axes = figure_2d_t.NewFigureAndAxes(offline_version=True)
        # Fix drawer
        drawer.axes = axes
        drawer.dbe = DRAWING_CONTEXT
    canvas = figure.canvas

    sequence_length = sequence.__len__()
    for time_point in range(sequence_length):
        drawer.ShowFrame(time_point=time_point, should_draw=False)
        canvas.draw()
        content = nmpy.array(canvas.renderer.buffer_rgba())[:, :, :3]
        if SaveFrame is None:
            if output is None:
                output = nmpy.empty((*content.shape, sequence_length), dtype=nmpy.uint8)
            output[..., time_point] = content
        else:
            SaveFrame(content, time_point)

    pypl.close(fig=figure)  # To prevent remaining caught in event loop

    return output


def FigureAxesAndDrawer(
    figure_class: Union[Type[figure_t], Type[figure_2d_t]],
    drawer_class: Union[Type[s_drawer_t], Type[s_drawer_2d_t]],
    sequence: sequence_t,
    channel: str,
    with_segmentation: bool,
    with_cell_labels: bool,
    with_track_labels: bool,
    dbe: context_t,
    offline: bool,
) -> Tuple[Union[figure_t, figure_2d_t], axes_2d_t, Union[s_drawer_t, s_drawer_2d_t]]:
    """"""
    figure, axes = figure_class.NewFigureAndAxes(offline_version=offline)
    drawer = drawer_class.NewForChannels(
        sequence,
        dbe,
        channel=channel,
        with_segmentation=with_segmentation,
        with_cell_labels=with_cell_labels,
        with_track_labels=with_track_labels,
        with_ticks=False,
        with_colorbar=False,
        in_axes=axes,
    )

    return figure, axes, drawer
