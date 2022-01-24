from itertools import product
import functools
from typing import List, Tuple, Dict, Set, Iterator, Iterable
import numpy as np
from ase import Atoms
from ase.geometry import wrap_positions
from clease.datastructures import FourVector, Figure
from .cluster import Cluster
from .cluster_fingerprint import ClusterFingerprint

__all__ = ('ClusterGenerator', 'SitesWithinCutoff')


class ClusterGenerator:
    """
    Class for generating cluster info that is independent of the
    template
    """

    def __init__(self, prim_cell: Atoms) -> None:
        self.with_cutoff = SitesWithinCutoff(self)
        self.prim = prim_cell

    @property
    def prim(self) -> Atoms:
        return self._prim

    @prim.setter
    def prim(self, other: Atoms) -> None:
        if not isinstance(other, Atoms):
            raise TypeError("prim must be an Atoms object")
        self._prim = other
        # Get the transposed cell as a contiguous array
        self.prim_cell_T = np.array(other.get_cell().T)
        self.prim_cell_invT = np.linalg.inv(self.prim_cell_T)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ClusterGenerator):
            return NotImplemented

        return np.allclose(self.prim_cell_invT, other.prim_cell_invT) and self.prim == other.prim

    def eucledian_distance_vec(self, x1: FourVector, x2: FourVector) -> np.ndarray:
        """
        Eucledian distance between to FourVectors in cartesian coordinates.

        :param x1: First vector
        :param x2: Second vector
        """

        euc1 = x1.to_cartesian(self.prim, transposed_cell=self.prim_cell_T)
        euc2 = x2.to_cartesian(self.prim, transposed_cell=self.prim_cell_T)
        return euc2 - euc1

    def to_four_vector(self, cartesian: np.ndarray, sublattice: int = None) -> FourVector:
        """Translate a position in Cartesian coordinates to its FourVector"""
        if not cartesian.ndim == 1:
            # XXX: This could instead return a List[FourVector] if we pass a 2d
            # set of coordinates.
            raise ValueError('Can only translate 1 position at a time.')

        if sublattice is None:
            sublattice = self.get_lattice(cartesian)
        cartesian = cartesian - self.prim.positions[sublattice, :]

        ix, iy, iz = np.round(self.prim_cell_invT.dot(cartesian)).astype(int)
        return FourVector(ix, iy, iz, sublattice)

    def to_cartesian(self, *four_vectors: FourVector) -> np.ndarray:
        """Convert one or more FourVectors into their Cartesian coordinates."""
        pos = np.zeros((len(four_vectors), 3))
        for ii, fv in enumerate(four_vectors):
            pos[ii, :] = fv.to_cartesian(self.prim, transposed_cell=self.prim_cell_T)
        return pos

    def get_lattice(self, pos: np.ndarray) -> int:
        """
        Return the corresponding sublattice of a cartesian position

        :param pos: array of length 3 Cartesian position
        """
        shifts = self.prim.get_positions()
        reshaped = np.reshape(pos, (1, 3))
        wrapped = wrap_positions(reshaped, self.prim.get_cell())
        diff_sq = np.sum((wrapped[0, :] - shifts)**2, axis=1)
        return int(np.argmin(diff_sq))

    def eucledian_distance(self, x1: FourVector, x2: FourVector) -> float:
        d = self.eucledian_distance_vec(x1, x2)
        return np.linalg.norm(d, ord=2)

    @property
    def shortest_diag(self) -> float:
        shortest = None
        cellT = self.prim.get_cell().T
        for w in product([-1, 0, 1], repeat=3):
            if all(x == 0 for x in w):
                continue

            diag = cellT.dot(w)
            length: float = np.sqrt(np.sum(diag**2))
            if shortest is None or length < shortest:
                shortest = length
        assert shortest is not None
        return shortest

    @property
    def num_sub_lattices(self) -> int:
        return len(self.prim)

    def sites_within_cutoff(self, cutoff: float, x0: FourVector) -> Iterable[FourVector]:
        min_diag = self.shortest_diag
        max_int = int(cutoff / min_diag) + 1

        def filter_func(fv: FourVector) -> bool:
            d = self.eucledian_distance(x0, fv)
            return 1E-5 < d < cutoff

        all_sites = product(range(-max_int, max_int + 1), range(-max_int, max_int + 1),
                            range(-max_int, max_int + 1), range(self.num_sub_lattices))

        return filter(filter_func, (FourVector(*site) for site in all_sites))

    def get_fp(self, figure: Figure) -> ClusterFingerprint:
        """Generate finger print for a Figure object.

        Args:
            figure (Figure): The figure to find the finger print from.

        Returns:
            ClusterFingerprint: The finger print of the cluster.
        """
        X = figure.to_cartesian(self.prim, transposed_cell=self.prim_cell_T)
        return positions_to_fingerprint(X)

    def prepare_within_cutoff(self, cutoff: float,
                              lattice: int) -> Dict[FourVector, Set[FourVector]]:
        """Prepare all sites which are within the cutoff sphere. Note, this only prepares sites
        which are pair-wise within the cutoff, and does not consider the distance to the
        center-of-mass. This needs to be checked for the individual figure which is created from
        these sites."""

        within_cutoff = {}
        x0 = FourVector(0, 0, 0, lattice)
        sites = set(self.with_cutoff.get(cutoff, lattice))
        within_cutoff[x0] = sites
        for s in sites:
            nearby = set(s1 for s1 in sites if s1 != s and self.eucledian_distance(s1, s) <= cutoff)

            within_cutoff[s] = nearby
        return within_cutoff

    def figure_iterator(self, size: int, cutoff: float, ref_lattice: int) -> Iterator[Figure]:
        """Iterate all possible figures of a given size, cutoff radius, and reference lattice.
        All figures are guaranteed to have a radius smaller than the cutoff radius.

        Args:
            size (int): Size of the clusters to be generated, e.g. 2 for 2-body clusters.
            cutoff (float): Cutoff sphere from the center of mass of the cluster.
            ref_lattice (int, optional): Site which clusters are generated from. Any cluster
            always contains this site.

        Yields:
            Iterator[Figure]: Iterable with all acceptable figures.
        """

        def is_figure_ok(figure: Figure, cutoff: float) -> bool:
            """Does the figure obey the cutoff radius?
            The diameter can be larger than the maximum distance between two atoms
            in the cluster, and so the site_iterator can prepare clusters with too large
            diameters.

            Returns:
                bool: The diameter of the cluster is within the cutoff
            """
            return figure.get_diameter(self.prim, transposed_cell=self.prim_cell_T) < cutoff

        cutoff_lut = self.prepare_within_cutoff(cutoff, ref_lattice)
        # Function which filters figures based on the cutoff diameter from the center of mass
        filter_func = functools.partial(is_figure_ok, cutoff=cutoff)
        return filter(filter_func, site_iterator(cutoff_lut, size, ref_lattice))

    def generate(self, size: int, cutoff: float,
                 ref_lattice: int) -> Tuple[List[List[Figure]], List[ClusterFingerprint]]:
        """Generate all possible figures of a given size, are within a given cutoff radius
        (from the center of mass of the figure), and from a reference lattice.

        Args:
            size (int): Size of the clusters to be generated, e.g. 2 for 2-body clusters.
            cutoff (float): Cutoff sphere from the center of mass of the cluster.
            ref_lattice (int, optional): Site which clusters are generated from. Any cluster
            always contains this site.

        Returns:
            List[List[Figure]], List[ClusterFingerprint]: The collection of figures and
                their corresponding fingerprints.
        """
        clusters: List[List[Figure]] = []
        all_fps: List[ClusterFingerprint] = []

        for new_figure in self.figure_iterator(size, cutoff, ref_lattice):
            # The entries in the figure must be ordered, due to equiv_sites
            # TODO: This ordereding should not be necessary.
            new_figure = self._order_by_internal_distances(new_figure)

            fp = self.get_fp(new_figure)

            # Find the group
            try:
                group = all_fps.index(fp)
                clusters[group].append(new_figure)
            except ValueError:
                # Does not exist, create a new group
                clusters.append([new_figure])
                all_fps.append(fp)

        return clusters, all_fps

    def _get_internal_distances(self, figure: Figure) -> List[List[float]]:
        """
        Return all the internal distances of a figure
        """
        dists = []
        for x0 in figure.components:
            tmp_dist = []
            for x1 in figure.components:
                dist = self.eucledian_distance(x0, x1)
                # float() to ensure we're not working on a NumPy floating number
                dist = round(float(dist), 6)
                tmp_dist.append(dist)
            dists.append(sorted(tmp_dist, reverse=True))
        return dists

    def _order_by_internal_distances(self,
                                     figure: Figure) \
            -> Figure:
        """Order the Figure by internal distances. Returns a new instance of the Figure."""
        dists = self._get_internal_distances(figure)
        fvs = figure.components
        zipped = sorted(list(zip(dists, fvs)), reverse=True)
        return Figure((x[1] for x in zipped))

    def to_atom_index(self, cluster: Cluster, lut: Dict[FourVector, int]) -> List[List[int]]:
        """
        Convert the integer vector representation to an atomic index

        :param clusters: List of clusters (in integer vector representation)

        :param template: Template atoms to use

        :param lut: Look up table for 4-vectors to indices
        """
        # pylint: disable=no-self-use
        return [[lut[fv] for fv in fig.components] for fig in cluster.figures]

    def equivalent_sites(self, figure: Figure) -> List[List[int]]:
        """Find the equivalent sites of a figure."""
        dists = self._get_internal_distances(figure)
        equiv_sites = []
        for i, d1 in enumerate(dists):
            for j in range(i + 1, len(dists)):
                d2 = dists[j]
                if np.allclose(d1, d2):
                    equiv_sites.append((i, j))

        # Merge pairs into groups
        merged: List[Set[int]] = []
        for equiv in equiv_sites:
            found_group = False
            for m in merged:
                if any(x in m for x in equiv):
                    m.update(equiv)
                    found_group = True
            if not found_group:
                merged.append(set(equiv))
        return [list(x) for x in merged]

    def get_max_distance(self, figure: Figure):
        """Return the maximum distance of a figure."""
        internal_dists = self._get_internal_distances(figure)
        max_dists = [x[0] for x in internal_dists]
        return max(max_dists)


class SitesWithinCutoff:
    """
    Class that keeps track of nearby sites. It automatically re-calculates if
    the cutoff changes. If it can re-use a previous result it will do that.
    """

    def __init__(self, generator: ClusterGenerator) -> None:
        self.generator = generator
        self.cutoff = 0.0
        # Dictionary mapping a ref lattice to a list of four-vectors
        self.pre_calc: Dict[int, List[FourVector]] = {}

    def must_generate(self, cutoff: float, ref_lattice: int) -> bool:
        """
        Check if we can re-use a precalculated result
        """
        if abs(cutoff - self.cutoff) > 1e-10:
            return True
        return ref_lattice not in self.pre_calc

    def get(self, cutoff: float, ref_lattice: int) -> List[FourVector]:
        """
        Return sites within the cutoff
        """
        if self.must_generate(cutoff, ref_lattice):
            sites = self.generator.sites_within_cutoff(cutoff, FourVector(0, 0, 0, ref_lattice))
            self.pre_calc[ref_lattice] = list(sites)
            self.cutoff = cutoff
        return self.pre_calc[ref_lattice]


def site_iterator(within_cutoff: Dict[FourVector, Set[FourVector]], size: int,
                  ref_lattice: int) -> Iterator[Figure]:
    """
    Return an iterator of all combinations of sites within a cutoff

    :param within_cutoff: Dictionary returned by `prepare_within_cutoff`

    :param size: Cluster size

    :param ref_lattice: Reference lattice
    """
    x0 = FourVector(0, 0, 0, ref_lattice)

    def recursive_yield(remaining, current):
        if len(current) == size - 1:
            # This is the full Figure object
            components = [x0] + current
            fig = Figure(components)
            yield fig
        else:
            for next_item in remaining:
                # Avoid double counting
                if any(next_item <= v for v in current):
                    continue
                rem = set.intersection(remaining, within_cutoff[next_item])
                yield from recursive_yield(rem, current + [next_item])

    for v in within_cutoff[x0]:
        rem = within_cutoff[x0].intersection(within_cutoff[v])
        yield from recursive_yield(rem, [v])


def positions_to_fingerprint(X: np.ndarray) -> ClusterFingerprint:
    """
    Generate finger print given a position matrix
    """
    # Center around the center of mass
    X = np.array(X)
    com = np.mean(X, axis=0)
    X -= com
    X = X.dot(X.T)
    # The positions squared
    diag_positions = np.diagonal(X)

    N = X.shape[0]
    # Put all the upper triangle off-diagonals into a 1D array one after another,
    # [off_diag1, off_diag2, ...]
    off_diag_len = N * (N - 1) // 2
    off_diag = np.zeros(off_diag_len)
    offset = 0
    for i in range(1, N):
        diag = np.diagonal(X, offset=i)
        off_diag[offset:(len(diag) + offset)] = diag
        offset += len(diag)
    # Sort positions, such that the largest position is first
    diag_positions = np.sort(diag_positions)[::-1]
    off_diag = np.sort(off_diag)
    # Append the off-diagonal elements after the diagonal, into a 1D array
    inner = np.append(diag_positions, off_diag)
    return ClusterFingerprint(fp=inner)
