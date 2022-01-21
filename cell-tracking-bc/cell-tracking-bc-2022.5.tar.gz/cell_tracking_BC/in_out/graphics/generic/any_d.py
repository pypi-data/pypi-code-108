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

from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as nmpy
import skimage.measure as msre

import cell_tracking_BC.standard.uid as uqid
from cell_tracking_BC.in_out.graphics.context import (
    _sg,
    annotation_h,
    axes_2d_t,
    axes_3d_t,
    rgb_color_h,
    rgba_color_h,
)
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.frame import frame_t
from cell_tracking_BC.type.segmentation import compartment_t
from cell_tracking_BC.type.sequence import sequence_h, sequence_t
from cell_tracking_BC.type.tracks import tracks_t


array_t = nmpy.ndarray


def AnnotateCells(
    frame: Union[array_t, frame_t],
    cell_contours: Optional[Sequence[array_t]],
    with_cell_labels: bool,
    cell_frame: Optional[frame_t],
    tracks: Optional[tracks_t],
    axes: Union[axes_2d_t, axes_3d_t],
    AnnotationStyle: _sg.cell_annotation_style_h,
    /,
    *,
    highlighted: int = -1,
    elevation: float = None,
    with_alpha_cell_uids: bool = True,
) -> Sequence[Tuple[int, Union[annotation_h, Sequence[annotation_h]]]]:
    """"""
    output = []

    if with_cell_labels or (tracks is not None):
        if elevation is None:
            axes.RemoveLinesAndAnnotations()

        if cell_frame is None:
            labeled = msre.label(frame, connectivity=1)
            cells = msre.regionprops(labeled)
        else:
            cells = cell_frame.cells
        assert hasattr(cells[0], "centroid") and hasattr(
            cells[0], "label"
        ), "Please contact developer about API change"

        for cell in cells:
            if elevation is None:
                position = nmpy.flipud(cell.centroid)
            else:
                position = (*cell.centroid, elevation)

            text = []
            if with_cell_labels:
                text.append(uqid.AlphaColumnFromLabel(cell.label))
            else:
                text.append("")
            if (tracks is None) or not isinstance(cell, cell_t):
                text.append("")
            else:
                labels = tracks.TrackLabelsContainingCell(cell, tolerant_mode=True)
                if labels is None:
                    text.append("?")
                else:
                    if labels.__len__() > 1:
                        labels = "\n".join(str(_lbl) for _lbl in labels)
                    else:
                        labels = str(labels[0])
                    text.append(labels)

            if with_alpha_cell_uids:
                text = "".join(text)
                additionals = AnnotationStyle(cell.label == highlighted, "\n" in text)
            else:
                if text[0].__len__() > 0:
                    multi_text = [(text[0], {})]
                else:
                    multi_text = []
                if text[1].__len__() > 0:
                    multi_text.extend(
                        (_pce, {"rotation": -90.0}) for _pce in text[1].split("\n")
                    )
                text = multi_text
                additionals = AnnotationStyle(cell.label == highlighted, False)

            annotation = axes.PlotCellAnnotation(position, text, **additionals)

            output.append((cell.label, annotation))

    # Leave this block after cell annotation since, if placed before, the (new) contours are considered as previous
    # artists and removed.
    if cell_contours is not None:
        if elevation is None:
            for contour in cell_contours:
                axes.PlotLines(
                    contour[:, 1],
                    contour[:, 0],
                    linestyle=":",
                    color=(0.0, 1.0, 1.0, 0.3),
                )
        else:
            for contour in cell_contours:
                heights = contour.shape[0] * [elevation]
                axes.PlotLines(
                    contour[:, 0],
                    contour[:, 1],
                    heights,
                    linestyle=":",
                    color=(0.0, 1.0, 1.0, 0.3),
                )

    return output


def CellContours(
    sequence: sequence_h, with_segmentation: bool, /
) -> Optional[Sequence[Sequence[array_t]]]:
    """"""
    if (
        with_segmentation
        and isinstance(sequence, sequence_t)
        and (sequence.segmentations is not None)
    ):
        output = []
        for segmentation in sequence.segmentations.CompartmentsWithVersion(
            compartment_t.CELL
        ):
            output.append(msre.find_contours(segmentation))
    else:
        output = None

    return output


def CellTracks(sequence: sequence_h, with_track_labels: bool, /) -> Optional[tracks_t]:
    """"""
    with_track_labels = (
        with_track_labels
        and isinstance(sequence, sequence_t)
        and (sequence.tracks is not None)
    )
    if with_track_labels:
        output = sequence.tracks
    else:
        output = None

    return output


def ColorAndAlpha(
    color: Union[str, rgb_color_h, rgba_color_h],
    NameToRGB: Callable[[str], rgb_color_h],
    /,
    *,
    convert_to_rgb: bool = False,
) -> Tuple[Union[str, rgb_color_h], Optional[float]]:
    """"""
    if (is_str := isinstance(color, str)) or (color.__len__() == 3):
        alpha = None
        if is_str and convert_to_rgb:
            color = NameToRGB(color)
    else:
        alpha = color[-1]
        color = color[:-1]

    return color, alpha


def ZeroOneValueToRGBAWithMilestones(
    value: Union[float, Sequence[float]],
    milestones: Sequence[Tuple[float, str]],
    NameToRGB: Callable[[str], rgb_color_h],
    /,
) -> Union[rgba_color_h, Sequence[rgba_color_h]]:
    """"""
    if isinstance(value, Sequence):
        return tuple(
            ZeroOneValueToRGBAWithMilestones(_vle, milestones, NameToRGB)
            for _vle in value
        )

    n_milestones = milestones.__len__()
    m_idx = 0
    while (m_idx < n_milestones) and (value > milestones[m_idx][0]):
        m_idx += 1
    if m_idx >= n_milestones:
        color = milestones[-1][1]
    elif value < milestones[m_idx][0]:
        if m_idx > 0:
            previous = m_idx - 1
        else:
            previous = 0
        interval = (milestones[previous][1], milestones[m_idx][1])
        interval = (NameToRGB(_clr) for _clr in interval)
        ratio = (value - milestones[previous][0]) / (
            milestones[m_idx][0] - milestones[previous][0]
        )
        color = tuple(
            ratio * _end + (1.0 - ratio) * _stt for _stt, _end in zip(*interval)
        )
    else:
        color = milestones[m_idx][1]

    if isinstance(color, str):
        color = NameToRGB(color)
    color = (*color, 1.0)

    return color
