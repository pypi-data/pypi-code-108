"""Crossover operations originally intended for medium sized particles"""
import random
import numpy as np
from ase import Atoms
from ase.ga.offspring_creator import OffspringCreator


class Crossover(OffspringCreator):
    """Base class for all particle crossovers.
    Do not call this class directly."""
    def __init__(self):
        OffspringCreator.__init__(self)
        self.descriptor = 'Crossover'
        self.min_inputs = 2


class SimpleCutSpliceCrossover(Crossover):
    """Crossover that divides two particles through a plane in space and
    merges the symbols of two halves from different particles together.
    The indexing of the atoms is preserved. Please only use this operator 
    with other operators that also preserves the indexing.

    It keeps the correct composition by randomly assigning elements in
    the new particle.

    Parameters
    ----------
    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    keep_composition : bool, default True
        Boolean that signifies if the composition should be the same 
        as in the parents.

    allowed_indices : list of ints, default None
        The indices of atoms that are allowed to be mutated by this 
        operator. All indices are considered if this is not specified.

    """

    def __init__(self, elements=None, 
                 keep_composition=True, 
                 allowed_indices=None):
        Crossover.__init__(self)
        self.elements = elements
        self.keep_composition = keep_composition
        self.allowed_indices = allowed_indices
        self.descriptor = 'SimpleCutSpliceCrossover'
        
    def get_new_individual(self, parents):
        f0, m0 = parents
        if self.allowed_indices is None:
            f, m = f0, m0
        else:
            f, m = f0[self.allowed_indices], m0[self.allowed_indices]
        indi = f.copy()

        theta = random.random() * 2 * np.pi  # 0,2pi
        phi = random.random() * np.pi  # 0,pi
        e = np.array((np.sin(phi) * np.cos(theta),
                      np.sin(theta) * np.sin(phi),
                      np.cos(phi)))
        eps = 0.0001
        
        f.translate(-f.get_center_of_mass())
        m.translate(-m.get_center_of_mass())
        
        # Get the signed distance to the cutting plane
        # We want one side from f and the other side from m
        if self.elements is not None:
            mids = [i for i, x in enumerate(f.get_positions()) if 
                    (np.dot(x, e) > 0) and (f[i].symbol in self.elements)]
        else:
            mids = [i for i, x in enumerate(f.get_positions()) if
                    np.dot(x, e) > 0]

        # Change half of f symbols to the half of m symbols
        for i in mids:
            indi[i].symbol = m[i].symbol

        # Check that the correct composition is employed
        if self.keep_composition:
            if self.elements is not None:
                fids = [i for i in range(len(f)) if (i not in mids)
                        and (f[i].symbol in self.elements)]
                opt_sm = sorted([a.number for a in f if 
                                 a.symbol in self.elements])
            else:
                fids = [i for i in range(len(f)) if i not in mids]
                opt_sm = sorted(f.numbers)
            tmpf_numbers = list(indi.numbers[fids])
            tmpm_numbers = list(indi.numbers[mids])
            cur_sm = sorted(tmpf_numbers + tmpm_numbers)
            # correct_by: dictionary that specifies how many
            # of the atom_numbers should be removed (a negative number)
            # or added (a positive number)
            correct_by = dict([(j, opt_sm.count(j)) for j in set(opt_sm)])
            for n in cur_sm:
                correct_by[n] -= 1
            correct_ids = random.choice([fids, mids])
            to_add, to_rem = [], []
            for num, amount in correct_by.items():
                if amount > 0:
                    to_add.extend([num] * amount)
                elif amount < 0:
                    to_rem.extend([num] * abs(amount))
            for add, rem in zip(to_add, to_rem):
                tbc = [i for i in correct_ids if indi[i].number == rem]
                if len(tbc) == 0:
                    pass
                ai = random.choice(tbc)
                indi[ai].number = add

        indi = self.initialize_individual(f, indi)
        if self.allowed_indices is not None:
            tmp = f0.copy()
            tmp.symbols[self.allowed_indices] = indi.symbols
            info = indi.info.copy()
            indi = tmp.copy()
            indi.info = info

        indi.info['data']['parents'] = [i.info['confid'] for i in parents] 
        indi.info['data']['operation'] = 'crossover'
        parent_message = ':Parents {0} {1}'.format(f.info['confid'],
                                                   m.info['confid'])
        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def get_numbers(self, atoms):
        """Returns the atomic numbers of the atoms object using only
        the elements defined in self.elements"""
        ac = atoms.copy()
        if self.elements is not None:
            del ac[[a.index for a in ac
                    if a.symbol in self.elements]]
        return ac.numbers
        
    def get_shortest_dist_vector(self, atoms):
        norm = np.linalg.norm
        mind = 10000.
        ap = atoms.get_positions()
        for i in range(len(atoms)):
            pos = atoms[i].position
            for j, d in enumerate([norm(k - pos) for k in ap[i:]]):
                if d == 0:
                    continue
                if d < mind:
                    mind = d
                    lowpair = (i, j + i)
        return atoms[lowpair[0]].position - atoms[lowpair[1]].position
