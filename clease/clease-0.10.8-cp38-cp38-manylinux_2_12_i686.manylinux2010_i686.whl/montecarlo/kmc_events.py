from typing import List
from abc import ABCMeta
from ase import Atoms
from ase.neighborlist import neighbor_list

__all__ = ('KMCEventType', 'NeighbourSwap')


class KMCEventType(metaclass=ABCMeta):

    @property
    def name(self):
        return type(self).__name__

    def get_swaps(self, atoms: Atoms, vac_idx: int) -> List[int]:
        raise NotImplementedError(f"get_swaps has not been implemented for class {self.name}")


class NeighbourSwap(KMCEventType):
    """
    KMC event that provides swaps between neighbours

    :param cutoff: Passed to ASE neighbour list. All sites
        within the cutoff are possible swaps
    """

    def __init__(self, atoms: Atoms, cutoff: float):
        super().__init__()
        first, second = neighbor_list('ij', atoms, cutoff)
        self.nl = [[] for _ in range(len(atoms))]
        for f, s in zip(first, second):
            self.nl[f].append(s)

    def get_swaps(self, atoms: Atoms, vac_idx: int) -> List[int]:
        return self.nl[vac_idx]
