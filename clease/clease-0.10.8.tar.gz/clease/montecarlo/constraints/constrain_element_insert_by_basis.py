import numpy as np
from .mc_constraint import MCConstraint


class ConstrainElementInserts(MCConstraint):
    """
    Constrain inserting the elements by basis. This constraint is intended
    to be used together with SGCMonteCarlo

    atoms: Atoms object
        ASE Atoms object used in the MC simulation

    index_by_basis: list
        Indices ordered by basis (same as `index_by_basis` parameter in
        `ClusterExpansionSettings`).
        If an Atoms object has 10 sites where the first 4 belongs to the
        first basis, the next 3 belongs to the next basis and the last 3
        belongs to the last basis, the `index_by_basis` would be
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

    element_by_basis: list
        List specifying which elements are allowed in each basis. If there are
        two basis where Si and O are allowed in the fist basis while Si and C
        are allowed in the second basis, the argument would be
        [['Si', 'O'], ['Si', 'C']]
    """

    def __init__(self, atoms, index_by_basis, element_by_basis):
        self.basis = np.zeros(len(atoms), dtype=int)
        for i, indices in enumerate(index_by_basis):
            for x in indices:
                self.basis[x] = i

        num_basis = len(element_by_basis)
        unique_elem = set(x for item in element_by_basis for x in item)
        self.element_allowed = {x: np.zeros(num_basis, dtype=np.uint8) for x in unique_elem}

        # Initialize the element lookup
        for i, elements in enumerate(element_by_basis):
            for elem in elements:
                self.element_allowed[elem][i] = 1

    def __call__(self, system_changes):
        for change in system_changes:
            indx = change[0]
            new_elem = change[2]
            basis = self.basis[indx]
            if self.element_allowed[new_elem][basis] == 0:
                return False
        return True
