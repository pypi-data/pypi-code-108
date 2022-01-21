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

import numbers as nmbr
import tempfile as temp
from pathlib import Path as path_t
from typing import Dict, Optional, Sequence, Union

import xlsxwriter as xlsx

from cell_tracking_BC.in_out.text.logger import LOGGER
from cell_tracking_BC.standard.uid import AlphaColumnFromIndex
from cell_tracking_BC.type.sequence import sequence_t


event_response_h = Dict[int, Optional[Sequence[float]]]
division_times_h = Dict[int, Sequence[int]]
death_time_h = Dict[int, int]


DASH_TYPES = (
    "solid",
    "round_dot",
    "square_dot",
    "dash",
    "dash_dot",
    "long_dash",
    "long_dash_dot",
    "long_dash_dot_dot",
)
N_DASH_TYPES = DASH_TYPES.__len__()


def SaveCellFeatureToXLSX(
    path: Union[str, path_t],
    sequence: sequence_t,
    /,
    *,
    feature: Union[str, Sequence[str]] = None,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if feature is None:
        features = sequence.available_cell_features
    elif isinstance(feature, str):
        features = (feature,)
    else:
        features = feature

    if path.exists():
        print(f"{path}: File (or folder) already exists...")
        path = path_t(temp.mkdtemp()) / path.name
        print(f"Using {path} instead")

    workbook = xlsx.Workbook(str(path))

    for feature in features:
        evolutions = sequence.FeatureEvolutionsAlongAllTracks(feature)
        first_label = tuple(evolutions.keys())[0]
        if not isinstance(evolutions[first_label][1][0], nmbr.Number):
            continue

        worksheet = workbook.add_worksheet(feature)
        rows_limits = {}
        for label, (track, evolution) in evolutions.items():
            worksheet.write_row(label - 1, track.root_time_point, evolution)
            rows_limits[label] = (
                track.root_time_point,
                track.root_time_point + evolution.__len__() - 1,
            )

        chart = workbook.add_chart({"type": "line"})
        for l_idx, (row, (min_col, max_col)) in enumerate(rows_limits.items()):
            min_col = AlphaColumnFromIndex(min_col)
            max_col = AlphaColumnFromIndex(max_col)
            chart.add_series(
                {
                    "name": str(row),
                    "values": f"='{feature}'!${min_col}${row}:${max_col}${row}",
                    "line": {
                        "width": 1.0,
                        "dash_type": DASH_TYPES[l_idx % N_DASH_TYPES],
                    },
                }
            )
        worksheet.insert_chart(f"A{max(rows_limits.keys()) + 1}", chart)

    workbook.close()


def SaveCellEventsToXLSX(
    path: Union[str, path_t],
    cell_division_frame_idc: Union[division_times_h, Dict[str, division_times_h]],
    cell_death_frame_idc: Union[death_time_h, Dict[str, death_time_h]],
    n_divisions: Union[int, Dict[str, int]],
    /,
    *,
    division_response: Union[
        event_response_h,
        Dict[str, event_response_h],
    ] = None,
    death_response: Union[
        event_response_h,
        Dict[str, event_response_h],
    ] = None,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if path.exists():
        print(f"{path}: File (or folder) already exists...")
        path = path_t(temp.mkdtemp()) / path.name
        print(f"Using {path} instead")

    workbook = xlsx.Workbook(str(path))

    for SaveEvents, event_time in zip(
        (_SaveDivisionEvents, _SaveDeathEvents),
        (cell_division_frame_idc, cell_death_frame_idc),
    ):
        if _IsSingleDictionary(event_time):
            SaveEvents(workbook, "", event_time)
        else:
            for suffix, contents in event_time.items():
                SaveEvents(workbook, "#" + suffix, contents)

    if isinstance(n_divisions, int) and _IsSingleDictionary(cell_death_frame_idc):
        _SaveEventCounts(workbook, "", n_divisions, cell_death_frame_idc)
    elif not (
        isinstance(n_divisions, int) or _IsSingleDictionary(cell_death_frame_idc)
    ):
        for suffix, dea_contents in cell_death_frame_idc.items():
            n_divisions_suffix = n_divisions[suffix]
            _SaveEventCounts(workbook, "#" + suffix, n_divisions_suffix, dea_contents)
    else:
        LOGGER.warn(
            f"{isinstance(n_divisions, int)}/{_IsSingleDictionary(cell_death_frame_idc)}: "
            f"Content type mismatch. Expected: Both single- (True), or both multi-content (False)."
        )

    for event, response in zip(
        ("division", "death"), (division_response, death_response)
    ):
        if response is None:
            continue

        if _IsSingleDictionary(response):
            _SaveEventResponse(event, workbook, "", response)
        else:
            for suffix, contents in response.items():
                _SaveEventResponse(event, workbook, "#" + suffix, contents)

    workbook.close()


def _SaveDivisionEvents(
    workbook: xlsx.Workbook,
    sheet_suffix: str,
    cell_division_frame_idc: division_times_h,
    /,
) -> None:
    """"""
    worksheet = workbook.add_worksheet(f"division times{sheet_suffix}")
    for label, divisions_idc in cell_division_frame_idc.items():
        if divisions_idc is not None:
            worksheet.write_row(label - 1, 0, divisions_idc)


def _SaveDeathEvents(
    workbook: xlsx.Workbook, sheet_suffix: str, cell_death_frame_idc: death_time_h, /
) -> None:
    """"""
    worksheet = workbook.add_worksheet(f"death time{sheet_suffix}")
    for label, death_idx in cell_death_frame_idc.items():
        if death_idx is not None:
            worksheet.write_number(label - 1, 0, death_idx)


def _SaveEventCounts(
    workbook: xlsx.Workbook,
    sheet_suffix: str,
    n_divisions: int,
    cell_death_frame_idc: death_time_h,
    /,
) -> None:
    """"""
    worksheet = workbook.add_worksheet(f"event counts{sheet_suffix}")

    n_deaths_pattern = 0
    n_deaths_track = 0
    for death_idx in cell_death_frame_idc.values():
        if death_idx is not None:
            if death_idx >= 0:
                n_deaths_pattern += 1
            else:
                n_deaths_track += 1

    for r_idx, (title, value) in enumerate(
        zip(
            ("divisions", "death (pattern)", "death (track)", "death"),
            (
                n_divisions,
                n_deaths_pattern,
                n_deaths_track,
                n_deaths_pattern + n_deaths_track,
            ),
        )
    ):
        worksheet.write_string(r_idx, 0, title)
        worksheet.write_number(r_idx, 1, value)


def _SaveEventResponse(
    event: str,
    workbook: xlsx.Workbook,
    sheet_suffix: str,
    responses: event_response_h,
    /,
) -> None:
    """"""
    name = f"{event} response{sheet_suffix}"
    worksheet = workbook.add_worksheet(name)
    rows_limits = {}
    for label, response in responses.items():
        if response is not None:
            worksheet.write_row(label - 1, 0, response)
            rows_limits[label] = response.__len__() - 1

    chart = workbook.add_chart({"type": "line"})
    for l_idx, (row, max_col) in enumerate(rows_limits.items()):
        max_col = AlphaColumnFromIndex(max_col)
        chart.add_series(
            {
                "name": str(row),
                "values": f"='{name}'!$A${row}:${max_col}${row}",
                "line": {"width": 1.0, "dash_type": DASH_TYPES[l_idx % N_DASH_TYPES]},
            }
        )
    worksheet.insert_chart(f"A{max(rows_limits.keys()) + 1}", chart)


def _IsSingleDictionary(dictionary: dict) -> bool:
    """"""
    return isinstance(tuple(dictionary.keys())[0], int)
