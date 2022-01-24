from typing import Sequence, Set, Dict, List
from itertools import product
from copy import deepcopy
import numpy as np
import ase
from ase.geometry import wrap_positions

from clease.datastructures import FourVector, Figure

from .cluster_fingerprint import ClusterFingerprint
from .cluster import Cluster
from .cluster_list import ClusterList
from .cluster_generator import ClusterGenerator
from .utils import name_clusters, size

__all__ = ('ClusterManager',)


class ClusterManager:
    """
    Manager for construction of all cluster.

    Parameters:

    prim_cell: ase.Atoms
        Primitive cell
    """

    def __init__(self, prim_cell: ase.Atoms, background_syms: Set[str] = None):
        self._background_syms = background_syms or set()

        primitive_filtered = self._filter_background(prim_cell)

        self.generator = ClusterGenerator(primitive_filtered)
        self.clusters = ClusterList()
        self._cache = _CacheChecker()

    @property
    def prim(self) -> ase.Atoms:
        """The primitive cell.
        Note, that background atoms have been removed from this atoms object."""
        return self.generator.prim

    @property
    def background_syms(self) -> Set[str]:
        """The symbols which are considered background."""
        return self._background_syms

    def _filter_background(self, atoms: ase.Atoms) -> ase.Atoms:
        """Filter the background atoms from an ASE Atoms object.

        Returns a copy of the original atoms object.
        """
        atoms = atoms.copy()

        # Find the indices we need to delete
        # If no background atoms are present, this will do nothing.
        delete = [atom.index for atom in atoms if self.is_background_atom(atom)]
        delete.sort(reverse=True)
        for i in delete:
            del atoms[i]
        return atoms

    def is_background_atom(self, atom: ase.Atom) -> bool:
        """Check whether an atom is a background atom."""
        return atom.symbol in self.background_syms

    def __eq__(self, other):
        return self.clusters == other.clusters and \
            self.generator == other.generator

    def _prepare_new_build(self, max_cluster_dia):
        """Prepare for a new call to ``build``
        """
        # Update the cache
        self._cache.set_cache(max_cluster_dia)
        # Clear any old clusters
        self.clusters.clear()

    def requires_build(self, max_cluster_dia: Sequence[float]) -> bool:
        """Check if the cluster manager requires a new build
        for a given set of cluster diameters"""
        return self._cache.requires_build(max_cluster_dia)

    def build(self, max_cluster_dia: Sequence[float]) -> None:
        """
        Construct all clusters.

        Parameters:

        max_cluster_dia: sequence of floats
            Maximum distance between two atoms in a cluster,
            for each cluster body. The diameters start at 2-body clusters
        """
        # Check if we already built the clusters with these settings
        if not self.requires_build(max_cluster_dia):
            return
        # We got a new set of settings, prepare to construct new clusters
        self._prepare_new_build(max_cluster_dia)

        # Number of lattices from 0 to N, where N
        # is the number of atoms in the primitive,
        # possibly without the background atoms.
        num_lattices = range(len(self.prim))
        all_fps: List[ClusterFingerprint] = []
        all_figures: List[List[Figure]] = []
        lattices = []

        for ref_lattice, (indx, diameter) in product(num_lattices, enumerate(max_cluster_dia)):
            cluster_size = indx + 2  # Size of cluster, start with 2-body at index 0
            figures, fps = self.generator.generate(cluster_size, diameter, ref_lattice)

            all_fps += fps
            all_figures += figures
            lattices += [ref_lattice] * len(figures)

        names = self._get_names(all_fps)
        # Transfer to the cluster list
        for figures, fp, name, ref_lattice in zip(all_figures, all_fps, names, lattices):
            # All figures are of the same size
            cluster_size = figures[0].size
            # Calculate the diameter from the first Figure, since they are all
            # geometrically equivalent, and thus have the same diameter.
            diameter = figures[0].get_diameter(self.prim)
            eq_sites = self.generator.equivalent_sites(figures[0])

            cluster = Cluster(name=name,
                              size=cluster_size,
                              diameter=diameter,
                              fingerprint=fp,
                              figures=figures,
                              equiv_sites=eq_sites,
                              group=ref_lattice)
            self.clusters.append(cluster)

        # Add singlets
        for i in range(len(self.prim)):
            self.clusters.append(
                Cluster(name='c1',
                        size=1,
                        diameter=0.0,
                        fingerprint=ClusterFingerprint([1.0]),
                        figures=[Figure([FourVector(0, 0, 0, i)])],
                        equiv_sites=[],
                        group=i))
        # Add empty
        self.clusters.append(
            Cluster(name='c0',
                    size=0,
                    diameter=0.0,
                    fingerprint=ClusterFingerprint([0.0]),
                    figures=[],
                    equiv_sites=[],
                    group=0))
        # Put the clusters in order of size. Has no practical effect,
        # but it looks nicer upon inspection.
        self.clusters.sort()

    @staticmethod
    def _get_names(all_fps: Sequence[ClusterFingerprint]):
        """
        Give a consistent name to all clusters

        Parameter:

        all_fps: list of ClusterFingerPrint
            A list with all the cluster fingerprints
        """
        # The following one-liner will do the job when we
        # decide to update cluster names from the legacy ones
        # where names where per by size
        # names = name_clusters(all_fps)

        sizes = sorted(set(size(fp) for fp in all_fps))
        names = [None for _ in all_fps]
        for s in sizes:
            fps = []
            indices = []
            for i, fp in enumerate(all_fps):
                if size(fp) == s:
                    indices.append(i)
                    fps.append(fp)
            names_per_size = name_clusters(fps)
            for i, n in zip(indices, names_per_size):
                names[i] = n
        return names

    def info_for_template(self, template: ase.Atoms) -> ClusterList:
        """
        Specialise the cluster information to a template

        Parameter:

        template: ase.Atoms
            Atoms object representing the simulation cell
        """
        unique = self.unique_four_vectors()
        lut = self.fourvec_to_indx(template, unique)
        ref_indices = [lut[FourVector(0, 0, 0, i)] for i in range(self.generator.num_sub_lattices)]

        cluster_int = deepcopy(self.clusters)
        for cluster in cluster_int:
            if cluster.size == 0:
                cluster.ref_indx = int(ref_indices[cluster.group])
                cluster.indices = []
            elif cluster.size == 1:
                cluster.ref_indx = int(ref_indices[cluster.group])
                cluster.indices = []
            else:
                cluster.indices = self.generator.to_atom_index(cluster, lut)
                cluster.ref_indx = int(ref_indices[cluster.group])
        return cluster_int

    def unique_four_vectors(self) -> Set[FourVector]:
        """
        Return a list with all unique 4-vectors which are
        represented in any figure in all of the clusters.
        """
        # We utilize that FourVector objects are hashable,
        # and therefore can be filtered using a set()
        unique = set()
        for cluster in self.clusters:
            if cluster.size == 0:
                continue
            for figure in cluster.figures:
                for fv in figure.components:
                    unique.add(fv)
        return unique

    def get_figures(self) -> List[ase.Atoms]:
        """
        Return a list of atoms object representing the clusters
        """
        return self.clusters.get_figures(self.generator)

    def create_four_vector_lut(self, template: ase.Atoms) -> Dict[FourVector, int]:
        """
        Construct a lookup table (LUT) for the index in template given the
        wrapped vector

        Parameter:

        template: Atoms
            Atoms object to use when creating the lookup table (LUT)
        """
        lut = {}
        pos = template.get_positions().copy()
        for i in range(pos.shape[0]):
            if self.is_background_atom(template[i]):
                # No need to make a lookup for a background atom
                continue
            vec = self.generator.to_four_vector(pos[i, :], template[i].tag)
            lut[vec] = i
        return lut

    def fourvec_to_indx(self, template: ase.Atoms,
                        unique: Sequence[FourVector]) -> Dict[FourVector, int]:
        """Translate a set of unique FourVectors into their corresponding index
        in a template atoms object."""
        cell = template.get_cell()
        pos = np.zeros((len(unique), 3))
        for i, fv in enumerate(unique):
            pos[i, :] = fv.to_cartesian(self.prim)

        pos = wrap_positions(pos, cell)
        unique_indices = []
        for i in range(pos.shape[0]):
            diff_sq = np.sum((pos[i, :] - template.get_positions())**2, axis=1)
            unique_indices.append(np.argmin(diff_sq))
        return dict(zip(unique, unique_indices))

    def translation_matrix(self, template: ase.Atoms) -> List[Dict[int, int]]:
        """
        Construct the translation matrix.

        The translation matrix translates a given atomic index to
        the corresponding atomic site if we started from index 0.

        Parameter:

        template: ase.Atoms
            Atoms object representing the simulation cell
        """
        trans_mat = []  # The final translation matrix list
        cell = template.get_cell()

        # Get the unique four-vectors which are present in all of our clusters.
        unique = self.unique_four_vectors()

        lut = self.create_four_vector_lut(template)
        cartesian = np.zeros((len(unique), 3))

        # Map the un-translated unique 4-vectors to their index
        unique_indx_lut = self.fourvec_to_indx(template, unique)
        # call int() to convert from NumPy integer to python integer
        unique_index = [int(unique_indx_lut[u]) for u in unique]

        for atom in template:
            if self.is_background_atom(atom):
                # This atom is considered a background, it has no mapping
                trans_mat.append({})
                continue

            # Translate the atom into its four-vector representation
            vec = self.generator.to_four_vector(atom.position, sublattice=atom.tag)

            # Translate the (x, y, z) components of the unique four-vectors
            # by this atom's (x, y, z) four-vector component
            translated_unique = [u.shift_xyz(vec) for u in unique]

            # Find the new Cartesian coordinates of the translated FourVectors,
            # and wrap them back into the cell
            cartesian = self.generator.to_cartesian(*translated_unique)
            cartesian = wrap_positions(cartesian, cell)

            # Re-translate the wrapped-Cartesian coordinates of the unique four-vectors
            # into a four-vector representation (with a generator expression)
            four_vecs = (self.generator.to_four_vector(cart, fv.sublattice)
                         for cart, fv in zip(cartesian, translated_unique))

            # Get the index of the translated four-vector
            indices = [lut[fv] for fv in four_vecs]

            trans_mat.append(dict(zip(unique_index, indices)))
        return trans_mat


class _CacheChecker:
    """Helper class to check if the
    cluster manager has already been built
    using a given set of settings.
    """

    def __init__(self):
        self.max_cluster_dia = None

    def requires_build(self, max_cluster_dia: Sequence[float]) -> bool:
        """Check if a given set of 'max_size'
        and 'max_cluster_dia' has previously been
        used to build the clusters"""
        # We don't have anything cached yet
        if self.max_cluster_dia is None:
            return True

        # Check if the parameters match
        return not np.array_equal(self.max_cluster_dia, max_cluster_dia)

    def set_cache(self, max_cluster_dia: Sequence[float]):
        # Ensure we set a copy, so no external
        # mutations affect the cache
        self.max_cluster_dia = deepcopy(max_cluster_dia)
