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
from abc import ABC as abc_t
from abc import abstractmethod
from typing import Any, Callable, ClassVar, Dict, Iterable, Iterator, List
from typing import Optional, Sequence, Tuple, Union

import networkx as grph

from cell_tracking_BC.standard.issue import ISSUE_SEPARATOR
from cell_tracking_BC.standard.number import MAX_INT
from cell_tracking_BC.standard.uid import ShortID
from cell_tracking_BC.type.cell import cell_t, state_t


TIME_POINT = "time_point"  # Leave it here (as opposed to making it a class variable) since it is used "everywhere"


class unstructured_track_t(grph.DiGraph):
    in_degree: Callable[[cell_t], int]
    out_degree: Callable[[cell_t], int]

    def Issues(self) -> Optional[Sequence[str]]:
        """"""
        output = []

        for cell in self.nodes:
            if (n_predecessors := self.in_degree(cell)) > 1:
                output.append(
                    f"Cell {cell.label}{ISSUE_SEPARATOR}{n_predecessors} predecessors. Expected=0 or 1."
                )

        if output.__len__() == 0:
            output = None

        return output

    def RootCellWithTimePoint(self) -> Tuple[cell_t, int]:
        """"""
        output = tuple(
            _rcd for _rcd in self.nodes.data(TIME_POINT) if self.in_degree(_rcd[0]) == 0
        )

        if (n_roots := output.__len__()) != 1:
            raise ValueError(f"{n_roots}: Invalid number of root cells; Expected=1")

        return output[0]

    def LeafCellsWithTimePoints(self) -> Tuple[Sequence[cell_t], Sequence[int]]:
        """"""
        # TODO: Contact the Networkx team about the following comment (or check code on github)
        #     /!\ It seems that networkx.DiGraph.nodes.data does not guarantee the node enumeration order. This could be
        #     inconvenient for reproducibility checks.
        records = (
            _rcd
            for _rcd in self.nodes.data(TIME_POINT)
            if self.out_degree(_rcd[0]) == 0
        )

        leaves, time_points = zip(*records)
        leaves = tuple(leaves)
        time_points = tuple(time_points)

        return leaves, time_points

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        time_points = grph.get_node_attributes(self, TIME_POINT)

        for edge in self.edges:
            time_point = time_points[edge[0]]
            is_last = self.out_degree(edge[1]) == 0
            yield time_point, *edge, is_last


@dtcl.dataclass(init=False, repr=False, eq=False)
class structured_track_t(abc_t):
    root: cell_t = None
    leaves: Sequence[cell_t] = None

    @property
    @abstractmethod
    def cells(self) -> Union[Iterable, Iterator]:
        """"""

    @property
    @abstractmethod
    def labels(self) -> Sequence[int]:
        """
        Single track labels
        """

    @property
    def labels_as_str(self) -> str:
        """
        Single track labels
        """
        return "+".join(str(_lbl) for _lbl in sorted(self.labels))

    @property
    def n_leaves(self) -> int:
        """"""
        return self.leaves.__len__()

    @property
    def lengths(self) -> Sequence[int]:
        """
        Segment-wise, not node-wise
        """
        return tuple(_ltp - self.root_time_point for _ltp in self.leaves_time_points)

    @property
    @abstractmethod
    def root_time_point(self) -> int:
        """"""

    @property
    @abstractmethod
    def leaves_time_points(self) -> Sequence[int]:
        """"""

    @abstractmethod
    def CellTimePoint(self, cell: cell_t) -> int:
        """"""

    @abstractmethod
    def CellSuccessors(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[cell_t]]:
        """
        Accounts for pruning
        """

    @abstractmethod
    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""

    @property
    @abstractmethod
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""

    @abstractmethod
    def Pieces(
        self, /, *, from_cell: cell_t = None, with_time_point: int = None
    ) -> Sequence[single_track_t]:
        """"""

    @property
    def single_tracks_iterator(self) -> Iterator[single_track_t]:
        """"""
        for leaf in self.leaves:
            yield self.TrackWithLeaf(leaf, check=False)

    @abstractmethod
    def TrackLabelsContainingCell(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[int]]:
        """"""

    @abstractmethod
    def TrackLabelWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[int]:
        """"""

    @abstractmethod
    def TrackWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[single_track_t]:
        """"""

    @abstractmethod
    def AsSingleTrack(self) -> single_track_t:
        """"""

    def Prune(
        self,
        ShouldStartPruning: Callable[[int, cell_t, dict], bool],
        /,
        *,
        ShouldStopPruning: Callable[[int, cell_t, dict], bool] = None,
        start_arguments: Dict[str, Any] = None,
        stop_arguments: Dict[str, Any] = None,
        called_from_educated_code: bool = False,
    ) -> None:
        """
        ShouldSt*Pruning arguments: time point, cell, kwargs

        called_from_educated_code: A track might be entirely pruned out here. Since it cannot remove itself from its
        referring objects, this method must be called from a piece of code that can do it if needed. This parameter is
        meant to prevent an "accidental" call from some "uneducated" piece of code.
        """
        if not called_from_educated_code:
            raise ValueError(
                f"{self.Prune.__name__}: Must be called from a piece of code handling full pruning"
            )

        if start_arguments is None:
            start_arguments = {}
        if (ShouldStopPruning is not None) and (stop_arguments is None):
            stop_arguments = {}

        dividing_cells = self.DividingCells()
        for single in self.single_tracks_iterator:
            t_idx = 0

            pruning = ShouldStopPruning is not None
            while pruning and (t_idx < single.__len__()):
                cell = single[t_idx]
                if (cell in dividing_cells) or ShouldStopPruning(
                    t_idx, cell, **stop_arguments
                ):
                    # Pruning stops at the first dividing cell since pruning further would then make several tracks out
                    # of one.
                    pruning = False
                    if t_idx > 0:
                        self.root = cell
                else:
                    cell.state = state_t.pruned
                    t_idx += 1

            while t_idx < single.__len__():
                if ShouldStartPruning(t_idx, single[t_idx], **start_arguments):
                    for cell in single[t_idx:]:
                        cell.state = state_t.pruned
                    break
                t_idx += 1

        if not self.IsFullyPruned():
            leaves = []
            # Adding Iterable to the class inheritance silences this warning. However, forking tracks become
            # un-instantiable for it lacks an __iter__ method.
            for cell in self:
                if cell.state.IsActive() and (self.CellSuccessors(cell).__len__() == 0):
                    leaves.append(cell)
            self.leaves = leaves

    def IsFullyPruned(self) -> bool:
        """"""
        return self.root.state == state_t.pruned

    def __str__(self) -> str:
        """"""
        if hasattr(self, "nodes"):
            cells = self.nodes
        else:
            cells = self
        cell_labels = tuple(_cll.label for _cll in cells)

        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.labels=}\n"
            f"    {self.root_time_point=}\n"
            f"    {self.leaves_time_points=}\n"
            f"    {self.lengths=}\n"
            f"    {cell_labels}"
        )


@dtcl.dataclass(init=False, repr=False, eq=False)
class single_track_t(structured_track_t, List[cell_t]):
    _label: int = None  # Single track label
    _root_time_point: int = None
    affinities: Sequence[float] = None

    def __init__(self, *args, **kwargs) -> None:
        """"""
        list.__init__(self, *args, **kwargs)

    @classmethod
    def NewFromOrderedCells(
        cls,
        cells: Sequence[cell_t],
        affinities: Sequence[float],
        root_time_point: int,
        label: Optional[int],
        /,
    ) -> single_track_t:
        """
        This must be the only place where direct instantiation is allowed. Anywhere else, instantiation must be
        performed with this class method.

        label: Can be None only to accommodate the creation of branches as single tracks
        """
        instance = cls(cells)

        instance._label = label
        instance.root = instance[0]
        instance.leaves = (instance[-1],)
        instance._root_time_point = root_time_point
        instance.affinities = affinities

        return instance

    @property
    def cells(self) -> Union[Iterable, Iterator]:
        """"""
        return self

    @property
    def label(self) -> int:
        """"""
        return self._label

    @property
    def labels(self) -> Sequence[int]:
        """"""
        return (self.label,)

    @property
    def length(self) -> int:
        """
        Segment-wise, not node-wise
        """
        return self.lengths[
            0
        ]  # Do not use list length as it does not account for pruned parts

    @property
    def root_time_point(self) -> int:
        """"""
        return self._root_time_point

    @property
    def leaf(self) -> cell_t:
        """"""
        return self.leaves[0]

    @property
    def leaf_time_point(self) -> int:
        """"""
        return self.CellTimePoint(self.leaf)

    @property
    def leaves_time_points(self) -> Sequence[int]:
        """"""
        return (self.leaf_time_point,)

    def CellTimePoint(self, cell: cell_t) -> int:
        """"""
        return self.root_time_point + self.index(cell) - self.index(self.root)

    def CellSuccessors(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[cell_t]]:
        """"""
        if (not check) or (cell in self):
            where = self.index(cell)
            if where < self.__len__() - 1:
                successor = self[where + 1]
                if successor.state.IsActive():
                    output = (successor,)
                else:
                    output = ()
            else:
                output = ()

            return output

        if tolerant_mode:
            return None

        raise ValueError(f"{cell}: Cell not in track")

    def DividingCells(
        self, /, *, _: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        return ()

    def _unpruned_piece(self) -> single_track_t:
        """"""
        root_idx = self.index(self.root)
        leaf_idx = self.index(self.leaf)

        # Just slicing returns an object of type list
        output = self.__class__(self[root_idx : (leaf_idx + 1)])
        for field in dtcl.fields(self):
            setattr(output, field.name, getattr(self, field.name))

        return output

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        unpruned = self._unpruned_piece()

        n_cells = unpruned.__len__()
        for c_idx in range(1, n_cells):
            time_point = self.root_time_point + c_idx - 1
            is_last = c_idx == n_cells - 1
            yield time_point, *unpruned[(c_idx - 1) : (c_idx + 1)], is_last

    def Pieces(self, /, **_) -> Sequence[single_track_t]:
        """"""
        return (self._unpruned_piece(),)

    def TrackLabelsContainingCell(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[int]]:
        """"""
        if (not check) or (cell in self):
            return self.labels

        if tolerant_mode:
            return None

        raise ValueError(f"{cell}: Cell not in track")

    def TrackLabelWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[int]:
        """"""
        if (not check) or (leaf in self.leaves):
            return self.label

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    def TrackWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[single_track_t]:
        """"""
        if (not check) or (leaf in self.leaves):
            return self._unpruned_piece()

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    def AsSingleTrack(self) -> single_track_t:
        """"""
        return self._unpruned_piece()

    def AsRowsColsTimes(
        self, /, *, with_labels: bool = False
    ) -> Union[
        Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...]],
        Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...], Tuple[int, ...]],
    ]:
        """"""
        unpruned = self._unpruned_piece()
        n_cells = unpruned.__len__()

        rows, cols = tuple(zip(*(_cll.centroid.tolist() for _cll in unpruned)))
        times = tuple(range(self.root_time_point, self.root_time_point + n_cells))

        if with_labels:
            labels = tuple(_cll.label for _cll in unpruned)
            return rows, cols, times, labels

        return rows, cols, times


# Cannot be a dataclass due to in/out_degree declarations (which are only here to silence unfound attribute warnings)
class forking_track_t(structured_track_t, grph.DiGraph):
    """
    Affinities are stored as edge attributes
    """

    SINGLE_TRACK_LABEL: ClassVar[str] = "single_track_label"

    in_degree: Callable[[cell_t], int]
    out_degree: Callable[[cell_t], int]

    def __init__(self, *args, **kwargs) -> None:
        """"""
        grph.DiGraph.__init__(self, *args, **kwargs)

    @classmethod
    def NewFromUnstructuredTrack(
        cls, track: unstructured_track_t, next_single_track_label: int, /
    ) -> Tuple[forking_track_t, int]:
        """"""
        instance = cls(track)

        instance.root, _ = track.RootCellWithTimePoint()
        instance.leaves, _ = track.LeafCellsWithTimePoints()

        for label, leaf in enumerate(instance.leaves, start=next_single_track_label):
            # Adds attribute "forking_track_t.SINGLE_TRACK_LABEL" with value "label"
            # to leaf node indexed by "leaf" (not to the leaf itself).
            grph.set_node_attributes(
                instance,
                {leaf: label},
                name=forking_track_t.SINGLE_TRACK_LABEL,
            )

        return instance, next_single_track_label + instance.n_leaves

    @property
    def cells(self) -> Union[Iterable, Iterator]:
        """"""
        return self.nodes

    @property
    def labels(self) -> Sequence[int]:
        """"""
        output = []

        for leaf in self.leaves:
            label = self.nodes[leaf].get(forking_track_t.SINGLE_TRACK_LABEL)
            if label is None:
                current = leaf
                neighbors = tuple(self.neighbors(current))
                while neighbors.__len__() > 0:
                    current = neighbors[0]
                    neighbors = tuple(self.neighbors(current))
                label = self.nodes[current][forking_track_t.SINGLE_TRACK_LABEL]

            output.append(label)

        return output

    @property
    def root_time_point(self) -> int:
        """"""
        return self.CellTimePoint(self.root)

    @property
    def leaves_time_points(self) -> Sequence[int]:
        """"""
        return tuple(self.CellTimePoint(_lef) for _lef in self.leaves)

    @property
    def affinities(self) -> Sequence[float]:
        """"""
        output = []

        for piece in self.Pieces():
            output.extend(piece.affinities)

        return output

    def CellTimePoint(self, cell: cell_t) -> int:
        """"""
        return self.nodes[cell][TIME_POINT]

    def CellSuccessors(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[cell_t]]:
        """"""
        if (not check) or (cell in self):
            return tuple(_ngh for _ngh in self.neighbors(cell) if _ngh.state.IsActive())

        if tolerant_mode:
            return None

        raise ValueError(f"{cell}: Cell not in track")

    def DividingCells(
        self, /, *, with_time_point: bool = False
    ) -> Sequence[Union[cell_t, Tuple[cell_t, int]]]:
        """"""
        if with_time_point:
            output = (
                _rcd
                for _rcd in self.nodes.data(TIME_POINT)
                if (self.out_degree(_cll := _rcd[0]) > 1) and _cll.state.IsActive()
            )
        else:
            output = (
                _cll
                for _cll in self.nodes
                if (self.out_degree(_cll) > 1) and _cll.state.IsActive()
            )

        return tuple(output)

    @property
    def segments_iterator(self) -> Iterator[Tuple[int, cell_t, cell_t, bool]]:
        """"""
        time_points = grph.get_node_attributes(self, TIME_POINT)

        for edge in self.edges:
            if all(_cll.state.IsActive() for _cll in edge):
                time_point = time_points[edge[0]]
                is_last = edge[1] in self.leaves
                yield time_point, *edge, is_last

    def Pieces(
        self, /, *, from_cell: cell_t = None, with_time_point: int = None
    ) -> Sequence[single_track_t]:
        """"""
        output = []

        if from_cell is None:
            piece = [self.root]
            root_time_point = self.root_time_point
        else:
            if not from_cell.state.IsActive():
                raise ValueError(f"{from_cell}: Not an active cell")
            piece = [from_cell]
            root_time_point = with_time_point
        affinities = []

        while True:
            last_cell = piece[-1]

            if last_cell in self.leaves:
                neighbors = None
                n_neighbors = 0
            else:
                neighbors = self.CellSuccessors(last_cell, check=False)
                n_neighbors = neighbors.__len__()

            if n_neighbors == 0:
                label = self.TrackLabelWithLeaf(last_cell, check=False)
                output.append(
                    single_track_t.NewFromOrderedCells(
                        piece, affinities, root_time_point, label
                    )
                )
                break
            elif n_neighbors == 1:
                next_cell = neighbors[0]
                piece.append(next_cell)
                affinities.append(self[last_cell][next_cell]["affinity"])
            else:
                output.append(
                    single_track_t.NewFromOrderedCells(
                        piece, affinities, root_time_point, None
                    )
                )
                next_time_point = root_time_point + piece.__len__()
                for neighbor in neighbors:
                    pieces = self.Pieces(
                        from_cell=neighbor,
                        with_time_point=next_time_point,
                    )
                    for piece in pieces:
                        if piece[0] is neighbor:
                            cells = (last_cell,) + tuple(piece)
                            affinity = self[last_cell][neighbor]["affinity"]
                            affinities = (affinity,) + tuple(piece.affinities)
                            piece = single_track_t.NewFromOrderedCells(
                                cells,
                                affinities,
                                piece.root_time_point - 1,
                                piece.label,
                            )
                        output.append(piece)
                break

        return output

    def TrackLabelsContainingCell(
        self, cell: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[Sequence[int]]:
        """"""
        output = []

        if check and not cell.state.IsActive():
            raise ValueError(f"{cell}: Not an active cell")

        for leaf in self.leaves:
            try:
                _ = grph.shortest_path(self, source=cell, target=leaf)
            except grph.NetworkXNoPath:
                continue
            output.append(self.nodes[leaf][forking_track_t.SINGLE_TRACK_LABEL])

        if (not check) or (output.__len__() > 0):
            return output

        if tolerant_mode:
            return None

        raise ValueError(f"{cell}: Cell not in track")

    def TrackLabelWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[int]:
        """
        TrackLabelWithLeaf: Implicitly, it is SingleTrackLabelWithLeaf
        """
        if (not check) or (leaf in self.leaves):
            return self.nodes[leaf][forking_track_t.SINGLE_TRACK_LABEL]

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    def TrackWithLeaf(
        self, leaf: cell_t, /, *, check: bool = True, tolerant_mode: bool = False
    ) -> Optional[single_track_t]:
        """
        TrackWithLeaf: Implicitly, it is SingleTrackWithLeaf
        """
        if (not check) or (leaf in self.leaves):
            cells = grph.shortest_path(self, source=self.root, target=leaf)
            affinities = tuple(
                self[cells[_idx]][cells[_idx + 1]]["affinity"]
                for _idx in range(cells.__len__() - 1)
            )
            label = self.TrackLabelWithLeaf(leaf, check=False)
            output = single_track_t.NewFromOrderedCells(
                cells, affinities, self.root_time_point, label
            )

            return output

        if tolerant_mode:
            return None

        raise ValueError(f"{leaf}: Not a leaf cell")

    def AsSingleTrack(self) -> single_track_t:
        """"""
        output = [self.root]

        affinities = []
        while True:
            last_cell = output[-1]

            if last_cell in self.leaves:
                neighbors = None
                n_neighbors = 0
            else:
                neighbors = self.CellSuccessors(last_cell, check=False)
                n_neighbors = neighbors.__len__()

            if n_neighbors == 0:
                label = self.TrackLabelWithLeaf(last_cell, check=False)
                break
            elif n_neighbors == 1:
                next_cell = neighbors[0]
                output.append(next_cell)
                affinity = self[last_cell][next_cell]["affinity"]
                affinities.append(affinity)
            else:
                raise ValueError(
                    f"Attempt to convert the forking track with root {self.root} and "
                    f"{self.n_leaves} leaves into a single track"
                )

        output = single_track_t.NewFromOrderedCells(
            output, affinities, self.root_time_point, label
        )

        return output


structured_track_h = Union[single_track_t, forking_track_t]
any_track_h = Union[unstructured_track_t, structured_track_h]


def DivisionTimePoints(
    dividing_cells: Sequence[Tuple[cell_t, int]], /
) -> Tuple[Optional[Sequence[int]], int]:
    """"""
    division_time_points = tuple(_elm[1] for _elm in dividing_cells)
    if division_time_points.__len__() > 0:
        last_div_frm = division_time_points[-1] + 1
    else:
        division_time_points = None  # Used to be (-1,)
        last_div_frm = 0

    return division_time_points, last_div_frm


def BasicTrackIssues(
    track: structured_track_h,
    /,
    *,
    root_time_point_interval: Sequence[Optional[int]] = (0, 0),
    leaves_time_point_intervals: Sequence[Optional[Sequence[Optional[int]]]] = (
        (1, None),
        (1, None),
    ),
    min_lengths: Sequence[Optional[int]] = (1, 1),
    max_n_children: int = 2,
    can_touch_border: bool = False,
) -> Optional[Sequence[str]]:
    """
    All parameters: any limit can be ignored by setting it to None
    All intervals are inclusive.
    leaf_time_point_intervals and min_lengths: first element is for the shortest branch, the second is for the longest.
        For single tracks, both are the same.
    min_lengths: edge-wise lengths, inclusive
    max_n_children: inclusive
    """
    output = []

    if track.root.state == state_t.dead:
        output.append('Root cell has a "dead" state')

    mini, maxi = _IntervalWithDefaults(root_time_point_interval, 0, MAX_INT)
    if not (mini <= track.root_time_point <= maxi):
        output.append(
            f"{track.root_time_point}{ISSUE_SEPARATOR}Invalid root time point. Expected={mini}..{maxi}"
        )

    min_ltp = min(track.leaves_time_points)
    max_ltp = max(track.leaves_time_points)
    for value, ltp_interval, which in zip(
        (min_ltp, max_ltp), leaves_time_point_intervals, ("shortest", "longest")
    ):
        if ltp_interval is None:
            continue
        mini, maxi = _IntervalWithDefaults(ltp_interval, 0, MAX_INT)
        if not (mini <= value <= maxi):
            output.append(
                f"{value}{ISSUE_SEPARATOR}Invalid leaf time point of {which} branch. Expected={mini}..{maxi}"
            )

    min_lgh = track.lengths[0]
    max_lgh = track.lengths[-1]
    # _IntervalWithDefaults is used on a non-interval!
    min_lengths = _IntervalWithDefaults(min_lengths, 0, 0)
    for value, mini, which in zip(
        (min_lgh, max_lgh), min_lengths, ("shortest", "longest")
    ):
        if value < mini:
            output.append(
                f"{value}{ISSUE_SEPARATOR}Invalid (edge-wise) length of {which} branch. Expected>={mini}"
            )

    if isinstance(track, forking_track_t):
        for cell in track.nodes:
            if (n_children := track.out_degree(cell)) > max_n_children:
                output.append(
                    f"C{cell.label}T{track.CellTimePoint(cell)}{ISSUE_SEPARATOR}"
                    f"{n_children} successors. Expected=0..{max_n_children}"
                )

    if not can_touch_border:
        for cell in track.cells:
            if cell.touches_border:
                output.append(
                    f"C{cell.label}T{track.CellTimePoint(cell)}{ISSUE_SEPARATOR}Touches frame border"
                )

    if output.__len__() == 0:
        output = None

    return output


def _IntervalWithDefaults(
    interval: Sequence[Optional[int]], default_min: int, default_max: int, /
) -> Sequence[int]:
    """"""
    tvl_min, tvl_max = interval
    if tvl_min is None:
        tvl_min = default_min
    if tvl_max is None:
        tvl_max = default_max

    return tvl_min, tvl_max
