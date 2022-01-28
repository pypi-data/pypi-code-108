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
import itertools as ittl
from operator import attrgetter as GetAttribute
from operator import itemgetter as ItemAt


from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import networkx as grph
from numpy import ndarray as array_t

from cell_tracking_BC.standard.number import INFINITY_MINUS
from cell_tracking_BC.standard.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.track import (
    TIME_POINT,
    any_track_h,
    forking_track_t,
    single_track_t,
    structured_track_h,
    unstructured_track_t,
)


invalid_tracks_h = Dict[
    Type[any_track_h], List[Tuple[any_track_h, Union[str, Sequence[str]]]]
]
TrackIssues_h = Callable[
    [structured_track_h, dict], Optional[Union[str, Sequence[str]]]
]
DividingCells_h = Callable[
    [forking_track_t, bool], Sequence[Union[cell_t, Tuple[cell_t, int]]]
]


def _Invalids() -> invalid_tracks_h:
    """"""
    return {
        unstructured_track_t: [],
        single_track_t: [],
        forking_track_t: [],
    }


@dtcl.dataclass(repr=False, eq=False)
class tracks_t(List[structured_track_h]):

    invalids: invalid_tracks_h = dtcl.field(init=False, default_factory=_Invalids)

    @classmethod
    def NewFromUnstructuredTracks(cls, tracks: unstructured_tracks_t, /) -> tracks_t:
        """"""
        instance = cls()

        next_single_track_label = 1
        for unstructured in tracks.track_iterator:
            issues = unstructured.Issues()
            if issues is None:
                (
                    forking_track,
                    next_single_track_label,
                ) = forking_track_t.NewFromUnstructuredTrack(
                    unstructured, next_single_track_label
                )

                if forking_track.n_leaves > 1:
                    instance.append(forking_track)
                else:
                    single_track = forking_track.AsSingleTrack()
                    instance.append(single_track)
            else:
                # unstructured.graph["issues"] = issues  # Old, per-track issue storage
                instance.invalids[unstructured_track_t].append((unstructured, issues))

        return instance

    def RootCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = map(GetAttribute("root", "root_time_point"), self)
            # output = ((_tck.root, _tck.root_time_point) for _tck in self)
        else:
            output = map(GetAttribute("root"), self)
            # output = (_tck.root for _tck in self)

        return tuple(output)

    def DividingCells(
        self,
        /,
        *,
        with_time_point: bool = False,
        per_single_track: bool = False,
    ) -> Union[
        Sequence[Union[cell_t, Tuple[cell_t, int]]],
        Dict[int, Sequence[Union[cell_t, Tuple[cell_t, int]]]],
    ]:
        """"""
        output = []

        for track in self:
            if isinstance(track, forking_track_t):
                dividing = track.DividingCells(with_time_point=with_time_point)
                output.extend(dividing)

        if per_single_track:
            per_track = {}
            for track in self.single_tracks_iterator:
                if with_time_point:
                    dividing = filter(lambda _elm: _elm[0] in track, output)
                    dividing = sorted(dividing, key=ItemAt(1))
                else:
                    dividing = tuple(filter(lambda _elm: _elm in track, output))
                per_track[track.label] = dividing

            output = per_track
        elif with_time_point:
            output.sort(key=ItemAt(1))

        return output

    def FilteredDividingCells(
        self,
        division_responses: Dict[int, Optional[Union[array_t, Sequence[float]]]],
        lower_bound: float,
        /,
        *,
        with_time_point: bool = False,
    ) -> Dict[int, Sequence[Union[cell_t, Tuple[cell_t, int]]]]:
        """
        As a per-single-track dictionary
        """
        output = {}

        unfiltered = self.DividingCells(with_time_point=True, per_single_track=True)
        for label, divisions in unfiltered.items():
            filtered = []
            for cell, time_point in divisions:
                sibling_labels = self.TrackLabelsContainingCell(cell)
                highest_response = max(
                    division_responses[_lbl][time_point]
                    if (division_responses[_lbl] is not None)
                    and (division_responses[_lbl][time_point] is not None)
                    else INFINITY_MINUS
                    for _lbl in sibling_labels
                )
                if highest_response >= lower_bound:
                    if with_time_point:
                        filtered.append((cell, time_point))
                    else:
                        filtered.append(cell)

            output[label] = tuple(filtered)

        return output

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        leaves = []
        time_points = []
        for track in self:
            leaves.extend(track.leaves)
            time_points.extend(track.leaves_time_points)

        if with_time_point:
            return tuple(zip(leaves, time_points))

        return tuple(leaves)

    def TrackWithRoot(
        self, root: cell_t, /, *, tolerant_mode: bool = False
    ) -> Optional[structured_track_h]:
        """"""
        for track in self:
            if root is track.root:
                return track

        if tolerant_mode:
            return None

        raise ValueError(f"{root}: Not a root cell")

    def TrackWithLeaf(
        self, leaf: cell_t, /, *, tolerant_mode: bool = False
    ) -> Optional[single_track_t]:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        for track in self:
            for cell in track.leaves:
                if leaf is cell:
                    return track.TrackWithLeaf(cell, check=False)

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    @property
    def single_tracks_iterator(self) -> Iterator[single_track_t]:
        """"""
        for track in self:
            for single_track in track.single_tracks_iterator:
                yield single_track

    def TrackLabelsContainingCell(
        self, cell: cell_t, /, *, tolerant_mode: bool = False
    ) -> Optional[Sequence[int]]:
        """"""
        for track in self:
            if cell in track:
                return track.TrackLabelsContainingCell(cell, check=False)

        if tolerant_mode:
            return None

        raise ValueError(f"{cell}: Not a tracked cell")

    def TrackLabelWithLeaf(
        self, leaf: cell_t, /, *, tolerant_mode: bool = False
    ) -> Optional[int]:
        """
        TrackLabelWithLeaf: Implicitly, it is SingleTrackLabelWithLeaf
        """
        track = self.TrackWithLeaf(leaf, tolerant_mode=True)
        if track is not None:
            return track.label

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    def Prune(
        self,
        ShouldStartPruning: Callable[[int, cell_t, dict], bool],
        /,
        *,
        ShouldStopPruning: Callable[[int, cell_t, dict], bool] = None,
        start_arguments: Dict[str, Any] = None,
        stop_arguments: Dict[str, Any] = None,
    ) -> None:
        """"""
        t_idx = 0
        while t_idx < self.__len__():
            track = self[t_idx]
            track.Prune(
                ShouldStartPruning,
                ShouldStopPruning=ShouldStopPruning,
                start_arguments=start_arguments,
                stop_arguments=stop_arguments,
                called_from_educated_code=True,
            )
            if track.IsFullyPruned():
                self.invalids[track.__class__].append((track, "Fully pruned"))
                del self[t_idx]
            else:
                t_idx += 1

    def FilterOut(
        self,
        TrackIssues: TrackIssues_h,
        /,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        TrackIssues: Arguments are: track and (optional) keyword arguments; Returned value can be None, an str, or a
            sequence of str.
        kwargs: Passed to TrackIsInvalid as keyword arguments
        """
        t_idx = 0
        while t_idx < self.__len__():
            track = self[t_idx]
            issues = TrackIssues(track, **kwargs)
            if issues is None:
                t_idx += 1
            else:
                self.invalids[track.__class__].append((track, issues))
                del self[t_idx]

    def Print(self) -> None:
        """"""
        for track in self:
            print(track)

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}: {self.__len__()=}"
        )


class unstructured_tracks_t(grph.DiGraph):
    def AddTrackSegment(
        self,
        src_cell: cell_t,
        tgt_cell: cell_t,
        src_time_point: int,
        affinity: float,
        /,
    ) -> None:
        """"""
        time_point = {TIME_POINT: src_time_point}
        time_point_p_1 = {TIME_POINT: src_time_point + 1}
        self.add_node(src_cell, **time_point)
        self.add_node(tgt_cell, **time_point_p_1)
        self.add_edge(src_cell, tgt_cell, affinity=affinity)

    @property
    def track_iterator(self) -> Iterator[unstructured_track_t]:
        """"""
        for cells in grph.weakly_connected_components(self):
            track_view = self.subgraph(cells)
            # Copy or re-instantiation is necessary since the subgraph is a view
            yield unstructured_track_t(track_view)


def UniqueCellsFromPerSingleTrackOnes(
    per_single_track: Dict[int, Sequence[Union[cell_t, Tuple[cell_t, int]]]],
    /,
    *,
    should_remove_time_point: bool = False,
) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
    """"""
    cells = ittl.chain.from_iterable(per_single_track.values())
    if should_remove_time_point:
        cells = map(ItemAt(0), cells)

    return tuple(set(cells))
