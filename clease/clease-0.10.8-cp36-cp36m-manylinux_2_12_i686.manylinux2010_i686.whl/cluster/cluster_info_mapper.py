from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree as KDTree
from ase.geometry import wrap_positions
from .cluster_list import ClusterList

__all__ = ('AtomsNotContainedInLargeCellError', 'ClusterInfoMapper')


class AtomsNotContainedInLargeCellError(Exception):
    pass


class ClusterInfoMapper:
    """
    Class for accelerating the construction of cluster descriptors when
    the cluster descriptors are already known for a larger cell

    :param atoms: ASE Atoms object
        Large atoms cell

    :param trans_matrix: list of dict
        Translation matrix for the large cell

    :param cluster_list: ClusterList
        Cluster info the for the large cell
    """

    def __init__(self, atoms, trans_matrix, cluster_list):
        self.atoms = atoms
        self.trans_matrix = trans_matrix
        self.cluster_list = cluster_list
        self.tree = KDTree(self.atoms.get_positions())

    def _map_indices(self, small_atoms):
        """Map indices from large atoms to small."""
        tree = KDTree(small_atoms.get_positions())

        # Positions in large cell
        large_pos = self.atoms.get_positions()

        # Wrap these positions into the small cell
        large_pos = wrap_positions(large_pos, small_atoms.get_cell())

        # loop through small Atoms and find the closest atoms in large cell
        dist, index_map = tree.query(large_pos)
        assert np.all(dist < 1E-6)

        if len(list(set(index_map))) != len(small_atoms):
            raise AtomsNotContainedInLargeCellError("All indices not covered")
        return index_map

    def _map_cluster_info(self, index_map):
        """
        Map cluster info of the large cell to the corresponding cluster info
        of the small cell
        """
        new_cluster_list = ClusterList()

        for cluster in self.cluster_list:
            new_cluster = deepcopy(cluster)
            new_cluster.ref_indx = int(index_map[cluster.ref_indx])
            new_cluster.indices = [[int(index_map[x]) for x in sub] for sub in cluster.indices]
            new_cluster_list.append(new_cluster)
        return new_cluster_list

    def _map_trans_matrix(self, index_map):
        """Map translation matrix."""
        unique = list(set(index_map))
        new_tm = []

        for row in unique:
            row_large = np.where(index_map == row)[0][0]
            new_tm.append({
                int(index_map[k]): int(index_map[v])
                for k, v in self.trans_matrix[row_large].items()
            })
        return new_tm

    def map_info(self, small_atoms):
        """Map cluster info and translation matrix from the large host."""
        index_map = self._map_indices(small_atoms)
        new_info = self._map_cluster_info(index_map)
        new_tm = self._map_trans_matrix(index_map)
        return new_info, new_tm
