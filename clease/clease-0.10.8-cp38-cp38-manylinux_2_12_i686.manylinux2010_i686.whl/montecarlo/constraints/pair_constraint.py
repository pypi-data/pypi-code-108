from .mc_constraint import MCConstraint


class PairConstraint(MCConstraint):
    """
    Pair constraint is a constraint that prevents two species
    from being part of a pair cluster

    Parameters:

    elements: list
        List of symbols (e.g. [Al, X] or [X, X])

    pair_cluster: Cluster
        Instance of a the Cluster class. An instance of a cluster class can
        for instance be obtained from a ClusterExpansionSettings object
        via settings.cluster_list.get_by_name("c2_d000_0")[0]

    trans_matrix: list of dicts
        Translation matrix for indices. This can be obtained from the
        trans_matrix attribute of the ClusterExpansionSettings object

    atoms: Atoms object
        Atoms object used for MC calculations
    """

    def __init__(self, elements, pair_cluster, trans_matrix, atoms):
        self.elements = sorted(elements)
        self.pair_cluster = pair_cluster
        self.trans_mat = trans_matrix
        self.atoms = atoms

    def _check_one(self, idx):
        t_indx = self.trans_mat[idx]
        for figure in self.pair_cluster.indices:
            symbs = sorted([self.atoms[t_indx[j]].symbol for j in figure])
            if self.elements == symbs:
                return False
        return True

    def __call__(self, system_changes):
        # Introduce all changes
        for change in system_changes:
            self.atoms[change[0]].symbol = change[2]

        # Loop through all changes
        move_ok = True
        for change in system_changes:
            if not self._check_one(change[0]):
                move_ok = False
                break

        # Undo all changes
        for change in system_changes:
            self.atoms[change[0]].symbol = change[1]
        return move_ok
