"""Comparators meant to be used in symmetry-constrained genetic 
algorithm (SCGA)."""
import bisect


class GroupSizeComparator(object):
    """For each given element, compares the sorted sizes of the 
    user-divided groups that have the given element. Returns True 
    if the sizes are the same, False otherwise. Self-symmetry is 
    considered for particles.

    Parameters
    ----------
    groups : list of lists, default None
        The atom indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricClusterOrderingGenerator` 
        or `acat.build.ordering.SymmetricSlabOrderingGenerator` or
        `acat.build.adlayer.SymmetricPatternGenerator`. If not provided 
        here, please provide the groups in atoms.info['data']['groups'] 
        in all intial structures. This is useful to mix structures with 
        different group divisions in one GA.

    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    """

    def __init__(self, groups=None, elements=None):
        self.groups = groups
        self.elements = elements

    def looks_like(self, a1, a2):
        """ Return if structure a1 or a2 are similar or not. """

        if self.groups is None:                     
            groups1 = a1.info['data']['groups']
            if groups1 == a2.info['data']['groups']:
                groups = groups1
            else:
                return False 
        else:
            groups = self.groups
        size1_dict = {e: [] for e in self.elements}
        size2_dict = {e: [] for e in self.elements}

        for group in groups:
            e1 = a1[group[0]].symbol
            bisect.insort(size1_dict[e1], len(group))
            e2 = a2[group[0]].symbol
            bisect.insort(size2_dict[e2], len(group))

        return size1_dict == size2_dict
 

class GroupCompositionComparator(object):
    """Compares the elemental compositions of all user-divided groups. 
    Returns True if the numbers are the same, False otherwise. 
    Self-symmetry is not considered for particles.

    Parameters
    ----------
    groups : list of lists, default None
        The atom indices in each user-divided group. Can be obtained 
        by `acat.build.ordering.SymmetricClusterOrderingGenerator` 
        or `acat.build.ordering.SymmetricSlabOrderingGenerator` or
        `acat.build.adlayer.SymmetricPatternGenerator`. If not provided 
        here, please provide the groups in atoms.info['data']['groups'] 
        in all intial structures. This is useful to mix structures with 
        different group divisions in one GA. 

    elements : list of strs, default None
        Only take into account the elements specified in this list. 
        Default is to take all elements into account.

    tol : int, default 0
        The maximum number of groups with different elements that two 
        structures are still considered to be look alike.

    """

    def __init__(self, groups=None, elements=None, tol=0):
        self.groups = groups
        self.elements = elements
        self.tol = tol

    def looks_like(self, a1, a2):
        """ Return if structure a1 or a2 are similar or not. """

        if self.groups is None:                     
            groups1 = a1.info['data']['groups']
            if groups1 == a2.info['data']['groups']:
                groups = groups1
            else:
                return False 
        else:
            groups = self.groups
        elements = self.elements
        if self.elements is None:
            e = list(set(a1.get_chemical_symbols()))
        else:
            e = self.elements

        groups = self.groups.copy()
        sorted_elems = sorted(set(a1.get_chemical_symbols()))
        if e is not None and sorted(e) != sorted_elems:
            for group in groups:
                torem = []
                for i in group:
                    if a1[i].symbol not in e:
                        torem.append(i)
                for i in torem:
                    group.remove(i)

        diff = [g for g in groups if a1[g[0]].symbol != a2[g[0]].symbol]

        return len(diff) <= self.tol
