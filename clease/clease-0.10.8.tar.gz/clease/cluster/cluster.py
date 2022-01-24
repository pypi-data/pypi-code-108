from typing import Sequence, Dict, Any, List
from functools import total_ordering
import numpy as np
from ase import Atoms
import attr
from clease.datastructures import Figure
from clease.tools import equivalent_deco, list2str
from .cluster_fingerprint import ClusterFingerprint

__all__ = ('Cluster',)


@total_ordering
@attr.s(order=False, eq=False)
class Cluster:
    """A Cluster class, which collects multiple symmetry equivalent Figure objects,
    and related properties."""

    name: str = attr.ib()
    size: int = attr.ib()
    diameter: float = attr.ib()
    fingerprint: ClusterFingerprint = attr.ib(
        validator=attr.validators.instance_of(ClusterFingerprint))
    figures: Sequence[Figure] = attr.ib()
    equiv_sites: Sequence[Sequence[int]] = attr.ib()
    group: int = attr.ib()

    info: Dict[str, Any] = attr.ib(default=attr.Factory(dict))
    # "indices" are the integer index representation of the Figures.
    # therefore, "indices" and "ref_indx" depend on the currently active template,
    # and are subject to mutation.
    indices: Sequence[Sequence[int]] = attr.ib(default=None)
    ref_indx: int = attr.ib(default=None)

    @figures.validator
    def _validate_figures(self, attribute, value):
        """Verify that we have the correct type in the "figures" field."""
        # pylint: disable=unused-argument, no-self-use
        for ii, v in enumerate(value):
            if not isinstance(v, Figure):
                raise TypeError(f'All values must Figure type, got {value} '
                                f'of type {type(v)} in index {ii}.')

    @property
    def fp(self) -> ClusterFingerprint:
        """Alias for fingerprint, for compatibility."""
        return self.fingerprint

    def __lt__(self, other: 'Cluster') -> bool:
        """Less-than comparison operator."""
        if not isinstance(other, Cluster):
            return NotImplemented
        return self.fingerprint < other.fingerprint

    def __eq__(self, other: 'Cluster') -> bool:
        """Equals comparison operator."""
        if not isinstance(other, Cluster):
            return NotImplemented
        return self.fingerprint == other.fingerprint

    def equiv_deco(self, deco):
        return equivalent_deco(deco, self.equiv_sites)

    def todict(self) -> Dict[str, Any]:
        return attr.asdict(self)

    def is_subcluster(self, other) -> bool:
        """Check if the passed cluster is a subcluster of the current."""
        if len(self.indices) == 0:
            return True

        if len(self.indices[0]) >= len(other.indices[0]):
            return False

        return any(set(s1).issubset(s2) for s1 in self.indices for s2 in other.indices)

    def get_figure(self, primitive: Atoms, index: int = 0) -> Atoms:
        """Get figure from a ClusterGenerator object"""
        figure_four_vec = self.figures[index]
        positions = np.array([fv.to_cartesian(primitive) for fv in figure_four_vec.components])
        positions -= np.mean(positions, axis=0)
        symbols = [primitive[fv.sublattice] for fv in figure_four_vec.components]
        return Atoms(symbols, positions=positions)

    def get_figure_key(self, figure: Sequence[int]) -> str:
        """Return a key representation of the figure (in index representation)."""
        return list2str(self._order_equiv_sites(figure))

    def _order_equiv_sites(self, figure: Sequence[int]) -> List[int]:
        """Sort equivalent sites of a figure in index representation."""
        figure_cpy = list(figure)
        for eq_group in self.equiv_sites:
            equiv_indices = [figure[i] for i in eq_group]
            equiv_indices.sort()
            for count, i in enumerate(eq_group):
                figure_cpy[i] = equiv_indices[count]
        return figure_cpy

    @property
    def num_fig_occurences(self) -> Dict[str, int]:
        """Number of ocurrences for each figures."""
        occ_count = {}
        for figure in self.indices:
            key = self.get_figure_key(figure)
            current_num = occ_count.get(key, 0)
            occ_count[key] = current_num + 1
        return occ_count

    def corresponding_figure(self, ref_indx: int, target_figure: Sequence[int],
                             trans_matrix: List[Dict[int, int]]):
        """Find figures that correspond to another reference index.

        Parameters:

        ref_indx: int
            reference index

        target_figure: list of indices
            list of atomic indices that constitute the original figure before
            translating

        trans_matrix: list of dicts
            translation matrix
        """
        target_figure = self._order_equiv_sites(target_figure)
        for figure in self.indices:
            translated_figure = [trans_matrix[ref_indx][x] for x in figure]
            translated_figure = self._order_equiv_sites(translated_figure)
            if translated_figure == target_figure:
                return self._order_equiv_sites(figure)

        raise RuntimeError(f"There are no matching figure for ref_indx: "
                           f"{ref_indx} and figure: {target_figure}!")

    def get_all_figure_keys(self):
        return [self.get_figure_key(fig) for fig in self.indices]

    @property
    def multiplicity(self) -> int:
        return len(self.figures)
