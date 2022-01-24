from typing import List, Sequence, Optional
from ase import Atoms

__all__ = ('AtomsManager',)


class AtomsManager:
    """
    Manager class for the Atoms object used in a cluster expansion context.
    This class can return indices of the Atoms object grouped according to
    various schemes.

    :param atoms: ASE Atoms object
    """

    def __init__(self, atoms: Atoms = None) -> None:
        self.atoms = atoms

    @property
    def atoms(self) -> Atoms:
        return self._atoms

    @atoms.setter
    def atoms(self, other: Optional[Atoms]) -> None:
        if other is not None and not isinstance(other, Atoms):
            raise TypeError(('Trying to set atoms with a non-atoms object. '
                             f'Expected atoms, got {type(other)}'))
        self._atoms = other

    def __eq__(self, other: 'AtomsManager') -> bool:
        if not isinstance(other, AtomsManager):
            return NotImplemented

        return self.atoms == other.atoms

    def index_by_tag(self) -> List[List[int]]:
        """Return atomic indices that are grouped by their tags.

        This method assumes that all atoms are tagged and the tags are in a
        continuous sequence starting from 0.
        """

        tags = sorted(set(atom.tag for atom in self.atoms))
        ind_by_tag = [[] for _ in tags]

        for atom in self.atoms:
            ind_by_tag[atom.tag].append(atom.index)
        return ind_by_tag

    def index_by_symbol(self, symbols: List) -> List[List[int]]:
        """Group atomic indices by its atomic symbols.

        Example:

            If symbols = ['Au', 'Cu'], then indices where the indices of Au are
            returned as group 1 (first list in the nested list of indices) and
            the indices of Cu are returned as group 2 (second list in the
            nested list of indices).

            If symbols = ['Au, ['Cu', 'X'], 'Ag'], then indices of Au are
            returned as group 1, the indices of Cu and X are returned as group
            2 and the indices of Ag are returned as group 3.

        :param symbols: List of symbols that define a group
        """
        ind_by_symbol = [[] for _ in symbols]
        group_map = {}
        for i, item in enumerate(symbols):
            if isinstance(item, list):
                for x in item:
                    group_map[x] = i
            else:
                group_map[item] = i

        # Loop over indices
        for atom in self.atoms:
            ind_by_symbol[group_map[atom.symbol]].append(atom.index)
        return ind_by_symbol

    def unique_elements(self, ignore: Sequence[str] = ()) -> List[str]:
        """Return a list of symbols of unique elements.

        :param ignore: List of symbols to ignore in finding unique elements.
        """
        all_unique = set(self.atoms.symbols)
        return list(all_unique - set(ignore))

    def single_element_sites(self, allowed_elements: List[List[str]]) -> List[int]:
        """
        Return a list of sites that can only be occupied by a single element
        according to allowed_elements.

        :param allowed_elements: List of allowed elements on each site.
            `allowed_elements` takes the same format/style as
            `basis_elements` in settings (i.e., a nested list with each
            sublist containing a list of elements in a basis). It is assumed
            that the first elements in each group is present in self.atoms.
            For example, if `allowed_elements` is
            [['Au', 'Ag' 'X], ['Cu', 'X']] it means that all sites of the
            `self.atoms` must be occupied by either Au or Cu. All of the
            original sites occupied by Au can be occupied by Ag or X in cluster
            expansion, and all of the original sites occupied by Cu can be
            occupied by Cu or X in the cluster expansion.
        """
        single_site_symb = [x[0] for x in allowed_elements if len(x) == 1]
        single_sites = []
        for atom in self.atoms:
            if atom.symbol in single_site_symb:
                single_sites.append(atom.index)
        return single_sites
