from typing import Sequence, List
import random
import numpy as np


class SwapMoveIndexTracker:

    def __init__(self):
        self.tracker = {}
        self.index_loc = None
        self._last_move = []

    @staticmethod
    def _unique_symbols_from_atoms(atoms) -> List[str]:
        return sorted(set(atoms.symbols))

    @property
    def symbols(self) -> List[str]:
        return list(self.tracker.keys())

    @property
    def num_symbols(self) -> int:
        return len(self.tracker)

    def __repr__(self):
        str_repr = f"SwapMoveIndexTracker at {hex(id(self))}\n"
        str_repr += f"Symbols tracked: {self.symbols}\n"
        str_repr += f"Tracker info: {self.tracker}\n"
        return str_repr

    def init_tracker(self, atoms):
        """Initialize the tracker with the numbers."""
        symbols = self._unique_symbols_from_atoms(atoms)

        # Track indices of all symbols
        self.tracker = {symb: [] for symb in symbols}

        # Track the location in self.tracker of each index
        self.index_loc = np.zeros(len(atoms), dtype=int)
        for atom in atoms:
            self.tracker[atom.symbol].append(atom.index)
            self.index_loc[atom.index] = len(self.tracker[atom.symbol]) - 1

    def filter_indices(self, include: Sequence[int]):
        include_set = set(include)
        for s, idx in self.tracker.items():
            self.tracker[s] = list(set(idx).intersection(include_set))
            for i, num in enumerate(self.tracker[s]):
                self.index_loc[num] = i

        # Remove empty items
        self.tracker = {k: v for k, v in self.tracker.items() if v}

    def move_already_updated(self, system_changes):
        """Return True if system_changes have already been taken into account.

        Parameters:

        system_changes:
        """
        return system_changes == self._last_move

    def update_swap_move(self, system_changes):
        """Update the atoms tracker.

        Parameters:

        system_changes:
        """
        if self.move_already_updated(system_changes):
            # This change has already been updated!
            return
        self._last_move = system_changes
        indx1 = system_changes[0][0]
        indx2 = system_changes[1][0]
        symb1 = system_changes[0][1]
        symb2 = system_changes[0][2]

        # Find the locations of the indices
        loc1 = self.index_loc[indx1]
        loc2 = self.index_loc[indx2]

        # Update the tracker and the locations
        self.tracker[symb1][loc1] = indx2
        self.index_loc[indx2] = loc1

        self.tracker[symb2][loc2] = indx1
        self.index_loc[indx1] = loc2

    def undo_last_swap_move(self):
        """Undo last swap move."""
        if not self._last_move:
            return
        opposite_change = []
        for change in self._last_move:
            opposite_change.append((change[0], change[2], change[1]))

        self.update_swap_move(opposite_change)
        self._last_move = []

    def get_random_indx_of_symbol(self, symbol: str) -> int:
        return random.choice(self.tracker[symbol])
