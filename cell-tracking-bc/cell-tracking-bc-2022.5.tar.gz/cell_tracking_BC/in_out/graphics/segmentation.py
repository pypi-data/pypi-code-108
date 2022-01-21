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

from typing import Optional, Union

import cell_tracking_BC.in_out.graphics.generic.any_d as gnrc
import cell_tracking_BC.in_out.graphics.generic.three_d as gnr3
from cell_tracking_BC.in_out.graphics.context import axes_3d_t, context_t, figure_t
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.context import DRAWING_CONTEXT
from cell_tracking_BC.in_out.graphics.generic.two_d_sequence import s_viewer_2d_t
from cell_tracking_BC.type.segmentation import compartment_t
from cell_tracking_BC.type.segmentations import segmentations_t
from cell_tracking_BC.type.sequence import sequence_h, sequence_t


def ShowSegmentation(
    sequence: sequence_h,
    /,
    *,
    compartment: compartment_t = compartment_t.CELL,
    version: str = None,
    with_cell_labels: bool = True,
    with_track_labels: bool = True,
    mode: str = "2d+t",
    keep_every: int = 2,
    with_ticks: bool = True,
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[Union[figure_t, s_viewer_2d_t]]:
    """
    mode: see ShowSequence
    """
    output = None

    if mode == "2d+t":
        viewer = dbe.s_viewer_2d_t.NewForSegmentation(
            sequence,
            dbe,
            version=version,
            with_cell_labels=with_cell_labels,
            with_track_labels=with_track_labels,
            with_ticks=with_ticks,
        )
        if prepare_only:
            output = viewer
        else:
            viewer.Show(interactively=interactively, in_main_thread=in_main_thread)
    elif mode in ("mille-feuille", "tunnels"):
        if isinstance(sequence, (segmentations_t, sequence_t)):
            if isinstance(sequence, segmentations_t):
                segmentations = sequence
            else:
                segmentations = sequence.segmentations
            segmentations = segmentations.CompartmentsWithVersion(compartment)
        else:
            segmentations = sequence

        figure, axes = dbe.figure_3d_t.NewFigureAndAxes()
        axes: axes_3d_t
        if mode == "mille-feuille":
            if isinstance(sequence, sequence_t) and sequence.has_cells:
                cell_frames = sequence.cell_frames
            else:
                cell_frames = None
            tracks = gnrc.CellTracks(sequence, with_track_labels)
            gnr3.ShowFramesAsMilleFeuille(
                segmentations,
                None,
                with_cell_labels,
                cell_frames,
                tracks,
                axes,
                dbe.CellAnnotationStyle,
                keep_every=keep_every,
            )
        else:
            gnr3.ShowFramesAsTunnels(segmentations, axes, keep_every=keep_every)

        if prepare_only:
            output = figure
        else:
            figure.Show(interactively=interactively, in_main_thread=in_main_thread)
    else:
        raise ValueError(
            f'{mode}: Invalid mode; Expected="2d+t", "mille-feuille", "tunnels"'
        )

    return output
