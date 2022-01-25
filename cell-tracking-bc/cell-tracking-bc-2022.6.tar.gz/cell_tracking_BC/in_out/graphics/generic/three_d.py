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

from typing import Optional, Sequence

import numpy as nmpy

from cell_tracking_BC.in_out.graphics.context import _sg
from cell_tracking_BC.in_out.graphics.context import axes_3d_t as axes_t
from cell_tracking_BC.in_out.graphics.generic.any_d import AnnotateCells
from cell_tracking_BC.type.frame import frame_t
from cell_tracking_BC.type.tracks import tracks_t


array_t = nmpy.ndarray


_MILLEFEUILLE_ALPHA = 0.8


def ShowFramesAsMilleFeuille(
    frames: Sequence[array_t],
    cell_contours: Optional[Sequence[Sequence[array_t]]],
    with_cell_labels: bool,
    cell_frames: Optional[Sequence[frame_t]],
    tracks: Optional[tracks_t],
    axes: axes_t,
    CellAnnotationStyle: _sg.cell_annotation_style_h,
    /,
    *,
    keep_every: int = 2,
    n_levels: int = 1,
) -> None:
    """"""
    n_frames = frames.__len__()
    shape = frames[0].shape
    scaling = axes.__class__.MillefeuilleScaling(shape, n_frames)

    kept_frames = frames[::keep_every]
    min_intensity = min(nmpy.amin(_frm) for _frm in kept_frames)
    max_intensity = max(nmpy.amax(_frm) for _frm in kept_frames)
    intensity_range = max(1, max_intensity - min_intensity)

    all_rows, all_cols = nmpy.meshgrid(range(shape[0]), range(shape[1]), indexing="ij")
    for t_idx, frame in enumerate(frames):
        if t_idx % keep_every > 0:
            continue

        axes.PlotImageInZ(
            frame,
            all_rows,
            all_cols,
            n_levels,
            t_idx,
            scaling,
            min_intensity=min_intensity,
            intensity_range=intensity_range,
            alpha=_MILLEFEUILLE_ALPHA,
            cmap="gray",
        )

        if (cell_contours is not None) or with_cell_labels or (tracks is not None):
            if cell_contours is None:
                contours = None
            else:
                contours = cell_contours[t_idx]
            if cell_frames is None:
                cell_frame = None
            else:
                cell_frame = cell_frames[t_idx]

            _ = AnnotateCells(
                frame,
                contours,
                with_cell_labels,
                cell_frame,
                tracks,
                axes,
                CellAnnotationStyle,
                elevation=scaling * (t_idx + 0.2),
            )

    axes.SetTimeAxisProperties(n_frames - 1)


def ShowFramesAsTunnels(
    frames: Sequence[array_t],
    axes: axes_t,
    /,
    *,
    keep_every: int = 2,
    iso_value: float = 0.5,
) -> None:
    """"""
    volume = nmpy.array(frames)
    n_frames_all = frames.__len__()

    ShowFirstFrameAsFloor(frames[0], axes)

    axes.PlotIsosurface(
        volume,
        iso_value,
        should_be_capped=True,
        keep_every=keep_every,
        cmap="rainbow",
        lw=1,
    )
    axes.SetTimeAxisProperties(n_frames_all - 1)


def ShowFirstFrameAsFloor(frame: array_t, axes: axes_t, /) -> None:
    """"""
    shape = frame.shape
    all_rows, all_cols = nmpy.meshgrid(range(shape[0]), range(shape[1]), indexing="ij")

    min_intensity = nmpy.amin(frame)
    max_intensity = nmpy.amax(frame)
    intensity_range = max(1, max_intensity - min_intensity)

    axes.PlotImageInZ(
        frame,
        all_rows,
        all_cols,
        100,
        0.0,
        0.0,
        min_intensity=min_intensity,
        intensity_range=intensity_range,
        alpha=0.2,
        cmap="gray",
    )
