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

# TODO: this implementation is a temporary solution to plotting division and death events. It should be replaced with
#     two_d_feature.py in generic. This will also be the occasion to extract the axes_track of two_d_tracking, make it
#     something similar to the future two_d_feature, and turn them both into embeddable axes as is two_d_sequence.

from numbers import Real as number_t
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import matplotlib.lines as lins
import matplotlib.pyplot as pypl
import numpy as nmpy
from matplotlib.collections import PatchCollection as patches_t
from matplotlib.legend_handler import HandlerTuple as tuple_handler_t
from matplotlib.patches import Rectangle as rectangle_t

from cell_tracking_BC.in_out.text.logger import LOGGER


rectangle_info_h = Tuple[int, float, float, bool, bool]
ValueTransform_h = Optional[Union[float, Callable[[float], float]]]


DIVISION_MARKER = "3"
DEATH_MARKER = "x"
DIVISION_MARKER_SIZE = 60
DEATH_MARKER_SIZE = 30
N_SCORE_LEGEND_SHADES = 8

_RECTANGLE_TYPE_DIV = 0
_RECTANGLE_TYPE_DEA = 1
_RECTANGLE_TYPE_MIXED = 2

_rectangle = rectangle_t((0.0, 0.0), 1.0, 1.0, facecolor="red")
_RED_MATPLOTLIB = _rectangle.get_facecolor()
_rectangle.set_facecolor("blue")
_BLUE_MATPLOTLIB = _rectangle.get_facecolor()
_rectangle.set_facecolor("None")
_NO_COLOR_MATPLOTLIB = _rectangle.get_facecolor()


def ShowDivisionAndDeathEventResponses(
    cell_division_response: Dict[int, Sequence[float]],
    cell_death_response: Dict[int, Sequence[float]],
    cell_division_frame_idc: Dict[int, Optional[Sequence[int]]],
    cell_death_frame_idc: Dict[int, Optional[int]],
    sequence_length: int,
    /,
    *,
    ValueTransform: ValueTransform_h = None,
    zero_is_black: bool = True,
    show_as_barplot: bool = False,
    should_launch_event_loop: bool = True,
) -> None:
    """"""
    if show_as_barplot:
        track_height = 2
    else:
        track_height = 1
    max_label, div_values, dea_values, rectangles_w_details = _ValuesAndRectangles(
        cell_division_response,
        cell_death_response,
        cell_division_frame_idc,
        cell_death_frame_idc,
        show_as_barplot,
    )
    if rectangles_w_details.__len__() == 0:
        LOGGER.info("Empty division or death responses")
        return

    _SetRectanglesColorAndHeight(
        rectangles_w_details,
        div_values,
        dea_values,
        ValueTransform,
        zero_is_black,
        show_as_barplot,
    )
    events = _DivisionAndDeathEvents(rectangles_w_details)

    figure, axes = pypl.subplots()

    rectangles = tuple(_elm[0] for _elm in rectangles_w_details)
    edge_colors = tuple(_rct.get_edgecolor() for _rct in rectangles)
    face_colors = tuple(_rct.get_facecolor() for _rct in rectangles)
    rectangles = patches_t(rectangles, edgecolors=edge_colors, facecolors=face_colors)
    axes.add_collection(rectangles)
    if show_as_barplot:
        color = "k"
    elif zero_is_black:
        color = "w"
    else:
        color = "k"
    for what, size, where in events:
        axes.scatter(*where, c=color, marker=what, s=size)
    _SetAxesProperties(axes, sequence_length, max_label, track_height)
    _AddLegend(axes, zero_is_black)

    figure.tight_layout()
    if should_launch_event_loop:
        pypl.show()


def _ValuesAndRectangles(
    cell_division_response: Dict[int, Sequence[float]],
    cell_death_response: Dict[int, Sequence[float]],
    cell_division_frame_idc: Dict[int, Optional[Sequence[int]]],
    cell_death_frame_idc: Dict[int, Optional[int]],
    show_as_barplot: bool,
    /,
) -> Tuple[
    int,
    Sequence[float],
    Sequence[float],
    Sequence[Tuple[rectangle_t, rectangle_info_h]],
]:
    """"""
    max_label = max(max(cell_division_response.keys()), max(cell_death_response.keys()))
    div_values = []
    dea_values = []
    rectangles = []

    for (
        (label, division_response),
        death_response,
        division_time_points,
        death_frame_idx,
    ) in zip(
        cell_division_response.items(),
        cell_death_response.values(),
        cell_division_frame_idc.values(),
        cell_death_frame_idc.values(),
    ):
        if (division_response is None) and (death_response is None):
            continue

        if division_response is not None:
            div_values.extend(division_response)
        if death_response is not None:
            dea_values.extend(death_response)

        # Whether pattern-based or track-based
        death_occurred = death_frame_idx is not None

        # Could be inside an "if not show_as_barplot", but the IDE might complain about potentially uninitialized object
        rtype = _RECTANGLE_TYPE_MIXED
        if division_response is None:
            if show_as_barplot:
                rtype = _RECTANGLE_TYPE_DEA
            for t_idx, dea_value in enumerate(death_response):
                if dea_value is None:
                    # The trajectory does not start at time point 0
                    continue

                # Note: division_time_points is None if no divisions (used to be (-1,))
                # Note: division is checked despite the track having no division response because the sibling track
                # might have a response (if long enough) higher enough.
                dividing = (division_time_points is not None) and (
                    t_idx in division_time_points
                )
                # Detected by pattern matching (track ending => negative death frame index)
                dying = death_occurred and (t_idx == death_frame_idx)

                rectangle = _EventRectangle(t_idx, label, show_as_barplot)
                details = (rtype, 0.0, dea_value, dividing, dying)
                rectangles.append((rectangle, details))

                if dying:
                    break
        elif death_response is None:
            if show_as_barplot:
                rtype = _RECTANGLE_TYPE_DIV
            for t_idx, div_value in enumerate(division_response):
                if div_value is None:
                    # The trajectory does not start at time point 0
                    continue

                # Note: division_time_points is None if no divisions (used to be (-1,))
                dividing = (division_time_points is not None) and (
                    t_idx in division_time_points
                )

                rectangle = _EventRectangle(t_idx, label, show_as_barplot)
                details = (rtype, div_value, 0.0, dividing, False)
                rectangles.append((rectangle, details))
        else:
            for t_idx, (div_value, dea_value) in enumerate(
                zip(division_response, death_response)
            ):
                if div_value is None:
                    # The trajectory does not start at time point 0
                    if dea_value is not None:
                        raise ValueError(
                            f"{label}: Trajectory has a valid death response at time point {t_idx} "
                            f"whereas the division response is invalid"
                        )
                    continue

                # Note: division_time_points is None if no divisions (used to be (-1,))
                dividing = (division_time_points is not None) and (
                    t_idx in division_time_points
                )
                # Detected by pattern matching (track ending => negative death frame index)
                dying = death_occurred and (t_idx == death_frame_idx)

                rectangle = _EventRectangle(t_idx, label, show_as_barplot)
                if show_as_barplot:
                    details = (_RECTANGLE_TYPE_DEA, 0.0, dea_value, False, dying)
                    rectangles.append((rectangle, details))

                    rectangle = _EventRectangle(t_idx, label, show_as_barplot)
                    details = (_RECTANGLE_TYPE_DIV, div_value, 0.0, dividing, False)
                else:
                    details = (
                        _RECTANGLE_TYPE_MIXED,
                        div_value,
                        dea_value,
                        dividing,
                        dying,
                    )
                rectangles.append((rectangle, details))

                if dying:
                    break

    return max_label, div_values, dea_values, rectangles


def _EventRectangle(
    time_point: int,
    label: int,
    show_as_barplot: bool,
    /,
) -> rectangle_t:
    """"""
    if show_as_barplot:
        corner_y = 2.0 * label - 1.5
    else:
        corner_y = label - 0.5

    return rectangle_t((time_point, corner_y), 1.0, 1.0)


def _SetRectanglesColorAndHeight(
    rectangles: Sequence[Tuple[rectangle_t, rectangle_info_h]],
    div_values: Sequence[float],
    dea_values: Sequence[float],
    ValueTransform: ValueTransform_h,
    zero_is_black: bool,
    show_as_barplot: bool,
    /,
) -> None:
    """
    ValueTransform: if a number, then value <= ValueTransform => value <- 0.0
    """
    if ValueTransform is None:
        ValueTransform = lambda _vle: _vle
    elif isinstance(ValueTransform, number_t):
        threshold = float(ValueTransform)

        def _ValueTransform(_vle: float, /) -> float:
            if _vle <= threshold:
                return 0.0
            else:
                return _vle

        ValueTransform = _ValueTransform

    min_div_value, div_scaling = _MinimumAndScaling(div_values)
    min_dea_value, dea_scaling = _MinimumAndScaling(dea_values)

    for rectangle, (rtype, div_value, dea_value, dividing, dying) in rectangles:
        div = ValueTransform(div_scaling * (div_value - min_div_value))
        dea = ValueTransform(dea_scaling * (dea_value - min_dea_value))

        if show_as_barplot:
            if rtype == _RECTANGLE_TYPE_DEA:
                if zero_is_black:
                    color = (dea, 0.0, 0.0)
                else:
                    color = (1.0, 1.0 - dea, 1.0 - dea)
                rectangle.set_height(1.5 * dea)
                rectangle.set_facecolor(_NO_COLOR_MATPLOTLIB)
            else:
                if zero_is_black:
                    color = (0.0, 0.0, div)
                else:
                    color = (1.0 - div, 1.0 - div, 1.0)
                rectangle.set_height(1.5 * div)
                rectangle.set_facecolor(color + (0.3,))
            rectangle.set_edgecolor(color)
        else:
            if zero_is_black:
                color = (dea, 0.0, div)
            else:
                div_color = (1.0 - div, 1.0 - div, 1.0)
                dea_color = (1.0, 1.0 - dea, 1.0 - dea)
                color = nmpy.minimum(div_color, dea_color)
            rectangle.set_edgecolor(color)
            rectangle.set_facecolor(color)


def _DivisionAndDeathEvents(
    rectangles: Sequence[Tuple[rectangle_t, rectangle_info_h]],
    /,
) -> Sequence[Tuple[str, int, Sequence[float]]]:
    """"""
    output = []

    for rectangle, (*_, dividing, dying) in rectangles:
        if dividing or dying:
            where = tuple(_crd + 0.5 for _crd in rectangle.get_xy())
            if dividing:
                output.append((DIVISION_MARKER, DIVISION_MARKER_SIZE, where))
            if dying:
                output.append((DEATH_MARKER, DEATH_MARKER_SIZE, where))

    return output


def _MinimumAndScaling(values: Sequence[float], /) -> Tuple[float, float]:
    """"""
    if values.__len__() > 0:
        min_value = min(values)
        max_value = max(values)
        scaling = 1.0 / (max_value - min_value)
    else:
        min_value, scaling = 0.0, 1.0

    return min_value, scaling


def _SetAxesProperties(
    axes: pypl.Axes, sequence_length: int, max_label: int, track_height: int, /
) -> None:
    """"""
    axes.set_xlim(left=0, right=sequence_length)
    axes.set_ylim(bottom=0, top=track_height * max_label + 1)

    if track_height == 2:
        offset = -0.5
    else:
        offset = 0.0
    positions = range(1, max_label + 1, max(1, int(round(max_label / 10))))
    axes.yaxis.set_ticks(track_height * nmpy.array(positions) + offset)
    axes.yaxis.set_ticklabels(positions)


def _AddLegend(axes: pypl.Axes, zero_is_black: bool, /) -> None:
    """"""
    shades = nmpy.linspace(0.0, 1.0, num=N_SCORE_LEGEND_SHADES)

    if zero_is_black:
        DivisionColor = lambda _shd: (0.0, 0.0, _shd)
        DeathColor = lambda _shd: (_shd, 0.0, 0.0)
    else:
        DivisionColor = lambda _shd: (1.0 - _shd, 1.0 - _shd, 1.0)
        DeathColor = lambda _shd: (1.0, 1.0 - _shd, 1.0 - _shd)
    score_legends = [
        [
            rectangle_t(
                (0, 0),
                3.0,
                5.0,
                edgecolor=_NO_COLOR_MATPLOTLIB,
                facecolor=_Clr(_shd),
            )
            for _shd in shades
        ]
        for _Clr in (DivisionColor, DeathColor)
    ]

    event_legends = [
        lins.Line2D(
            (),
            (),
            color="k",
            marker=_mrk,
            markersize=_sze,
            linestyle="None",
        )
        for _mrk, _sze in (
            (DIVISION_MARKER, DIVISION_MARKER_SIZE // 5),
            (DEATH_MARKER, DEATH_MARKER_SIZE // 5),
        )
    ]

    axes.legend(
        handles=(*score_legends, *event_legends),
        labels=("Division Score", "Death Score", "Division", "Death (pattern)"),
        loc="right",
        bbox_to_anchor=(1.3, 0.5),
        handler_map={list: tuple_handler_t(ndivide=None, pad=0)},
    )
