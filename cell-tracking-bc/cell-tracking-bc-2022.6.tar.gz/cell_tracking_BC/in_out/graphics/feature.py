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

from cell_tracking_BC.in_out.file.archiver import archiver_t
from cell_tracking_BC.in_out.graphics.context import axes_2d_t, context_t, figure_t
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.context import DRAWING_CONTEXT
from cell_tracking_BC.type.sequence import sequence_t


def ShowCellFeatureEvolution(
    sequence: sequence_t,
    feature: str,
    /,
    *,
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    figure_name: str = "segmentation",
    dbe: context_t = DRAWING_CONTEXT,
    archiver: archiver_t = None,
) -> Optional[figure_t]:
    """"""
    output = None

    figure, axes = dbe.figure_2d_t.NewFigureAndAxes(title=feature)
    axes: axes_2d_t

    evolutions = sequence.FeatureEvolutionsAlongAllTracks(feature)
    max_track_length = 0
    for label, (track, evolution) in evolutions.items():
        axes.PlotLines(
            range(track.root_time_point, track.leaf_time_point + 1),
            evolution,
            label=label,
        )

        if track.length > max_track_length:
            max_track_length = track.length
    axes.SetTimeAxisProperties(max_track_length)
    axes.ShowLegend()

    figure.Archive(name=figure_name, archiver=archiver)
    if prepare_only:
        output = figure
    else:
        figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output
