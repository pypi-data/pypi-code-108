from typing import Sequence, List, Set, Tuple
import random
from abc import abstractmethod, ABC
from ase import Atoms
from clease.datastructures import SystemChange
from clease.tools import flatten
from .constraints import MCConstraint
from .swap_move_index_tracker import SwapMoveIndexTracker

__all__ = ('TrialMoveGenerator', 'RandomFlip', 'RandomSwap', 'MixedSwapFlip', 'TooFewElementsError',
           'RandomFlipWithinBasis')

DEFAULT_MAX_ATTEMPTS = 10000


class TooFewElementsError(Exception):
    """
    Error that indicates that there are too few elements to perform a certain operation on
    an atoms object. An example is a Monte Carlo step at fixed concentrations which consists
    of swapping to atoms. If there are less than 2 different species in the Atoms object, it
    makes no sense to swap two atoms (all energies are equal)
    """


class TrialMoveGenerator(ABC):
    """
    Class for producing trial moves.

    :param max_attempts: Maximum number of attempts to try to find a move that passes
        the constraints. If not constraints are added, this has no effect.
    """

    def __init__(self, max_attempts: int = DEFAULT_MAX_ATTEMPTS):
        super().__init__()
        self._constraints = []
        self.max_attempts = max_attempts

    def initialize(self, atoms: Atoms) -> None:
        """
        Initialize the generator.

        :param atoms: Atoms object used in the simulation
        """

    def remove_constraints(self) -> None:
        """
        Remove all constraints
        """
        self._constraints = []

    @property
    def name(self):
        return type(self).__name__

    def add_constraint(self, cnst: MCConstraint):
        """
        Add a constraint to the generator

        :param cnst: Constraint that must be satisfied for all trial moves
        """
        self._constraints.append(cnst)

    def _change_ok(self, system_changes: Sequence[SystemChange]) -> bool:
        for cnst in self._constraints:
            if not cnst(system_changes):
                return False
        return True

    @abstractmethod
    def get_single_trial_move(self) -> Sequence[SystemChange]:
        """
        Return a single trial move, must be implemented in sub-classes
        """

    def get_trial_move(self) -> Sequence[SystemChange]:
        """
        Produce a trial move that is consistent with all cosntraints
        """
        for _ in range(self.max_attempts):
            move = self.get_single_trial_move()
            if self._change_ok(move):
                return move
        raise RuntimeError("Can not produce a valid trial move")

    def on_move_accepted(self, changes: Sequence[SystemChange]) -> None:
        """
        Callback that is called by Monte Carlo after each accepted move

         :param change: Seqeunce of trial moves performed
        """

    def on_move_rejected(self, changes: Sequence[SystemChange]) -> None:
        """
        Callback that is called after a move is rejected

        :param change: Seqeunce of trial moves performed
        """


class SingleTrialMoveGenerator(TrialMoveGenerator, ABC):
    """
    Interface class for generators that return only one type of trial moves
    """
    CHANGE_NAME = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.CHANGE_NAME is None:
            raise ValueError("Subclasses must set CHANGE_NAME")

    def name_matches(self, change: SystemChange) -> bool:
        """
        Return true of the name of the passed system change matches
        the CHANGE_NAME attribute.

        :param change: a system change
        """
        return self.CHANGE_NAME == change.name

    def made_changes(self, changes: Sequence[SystemChange]) -> List[SystemChange]:
        """
        Extract the subset system changes made by an instance of itself.
        This method can be overrided in sublcasses, but the default behavior is
        to extract the subset of changes where the name matches.
        """
        return [change for change in changes if self.name_matches(change)]


class RandomFlip(SingleTrialMoveGenerator):
    """
    Generate trial moves where the symbol at a given site is flipped

    :param symbols: Set with all symbols considered in a move
    :param atoms: Atoms object for the simulation
    :param indices: List with all indices that should be considered. If None, all indices are
        considered
    """
    CHANGE_NAME = 'flip_move'

    def __init__(self, symbols: Set[str], atoms: Atoms, indices: List[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.symbols = symbols
        self.atoms = atoms

        if indices is None:
            self.indices = list(range(len(self.atoms)))
        else:
            self.indices = indices

    def get_single_trial_move(self) -> List[SystemChange]:
        pos = random.choice(self.indices)
        old_symb = self.atoms[pos].symbol
        new_symb = random.choice([s for s in self.symbols if s != old_symb])
        return [
            SystemChange(index=pos, old_symb=old_symb, new_symb=new_symb, name=self.CHANGE_NAME)
        ]


class RandomSwap(SingleTrialMoveGenerator):
    """
    Produce random swaps

    :param atoms: Atoms object in the MC simulation
    :param indices: List with indices that can be chosen from. If None, all indices
        can be chosen.
    """
    CHANGE_NAME = 'swap_move'

    def __init__(self, atoms: Atoms, indices: List[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.tracker = SwapMoveIndexTracker()
        self.indices = indices
        self.initialize(atoms)

    def initialize(self, atoms: Atoms) -> None:
        """
        Initializes the atoms tracker
        """
        self.tracker.init_tracker(atoms)
        if self.indices:
            self.tracker.filter_indices(self.indices)

        if self.tracker.num_symbols < 2:
            raise TooFewElementsError("After filtering there are less than two symbol type left. "
                                      "Must have at least two.")

    def get_single_trial_move(self) -> List[SystemChange]:
        """
        Create a swap move
        """
        symb_a = random.choice(self.tracker.symbols)
        symb_b = random.choice([s for s in self.tracker.symbols if s != symb_a])
        rand_pos_a = self.tracker.get_random_indx_of_symbol(symb_a)
        rand_pos_b = self.tracker.get_random_indx_of_symbol(symb_b)
        return [
            SystemChange(index=rand_pos_a, old_symb=symb_a, new_symb=symb_b, name=self.CHANGE_NAME),
            SystemChange(index=rand_pos_b, old_symb=symb_b, new_symb=symb_a, name=self.CHANGE_NAME)
        ]

    def on_move_accepted(self, changes: Sequence[SystemChange]):
        self.tracker.update_swap_move(changes)


class MixedSwapFlip(TrialMoveGenerator):
    """
    Class for generating trial moves in a mixed ensemble. A subset of the
    sites should maintain a constant concentrations, and a subset should
    maintain constant chemical potential. Thus, for the subset of sites
    where the concentration should be fixed, swap moves are proposed and
    for the subset that should have constant chemical potentia, flip moves
    are probosed (e.g. switching symbol type on a site)

    :param atoms: Atoms object used in the simulation
    :param swap_indices: List of indices that constitue the sub-lattice
        that should have fixed concentration
    :param flip_indices: List of indices that constitute the sub-lattice
        that should have fixed chemical potential
    :param flip_symbols: List of possible symbols that can be substituted
        on the lattice with fixed chemical potential.
    :param flip_prob: Probability of returning a flip move. The probability
        of returning a swap move is then 1 - flip_prob.
    """

    def __init__(self,
                 atoms: Atoms,
                 swap_indices: Sequence[int],
                 flip_indices: Sequence[int],
                 flip_symbols: Sequence[str],
                 flip_prob: float = 0.5,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.swapper = RandomSwap(atoms, swap_indices)
        self.flipper = RandomFlip(flip_symbols, atoms, flip_indices)
        self.flip_prob = flip_prob
        self.initialize(atoms)

    @property
    def generators(self) -> Tuple[SingleTrialMoveGenerator]:
        return (self.flipper, self.swapper)

    @property
    def weights(self) -> Tuple[float]:
        """The probability weights for each generator"""
        return (self.flip_prob, 1.0 - self.flip_prob)

    def initialize(self, atoms: Atoms) -> None:
        """
        Initialize the trial move generator
        """
        for gen in self.generators:
            gen.initialize(atoms)

    def get_single_trial_move(self) -> Sequence[SystemChange]:
        """
        Produce a single trial move. Return a swap move with
        probability
        """
        gen = random.choices(self.generators, weights=self.weights, k=1)[0]
        return gen.get_single_trial_move()

    def on_move_accepted(self, changes: Sequence[SystemChange]):
        """
        Callback triggered when a move have been accepted.
        """
        for gen in self.generators:
            gen_changes = gen.made_changes(changes)
            if gen_changes:
                gen.on_move_accepted(gen_changes)

    def on_move_rejected(self, changes: Sequence[SystemChange]) -> None:
        """
        Callback triggered when a move have been accepted.
        """
        for gen in self.generators:
            gen_changes = gen.made_changes(changes)
            if gen_changes:
                gen.on_move_rejected(gen_changes)


class RandomFlipWithinBasis(SingleTrialMoveGenerator):
    """
    Produce trial moves consisting of flips within each basis. Each basis
    is defined by a list of indices.

    Args:
        symbols: Sequence allowed symbols in each basis
        atoms: Atoms object to be used in the simulation for which the trial
            moves are produced
        indices: Sequence of sets of indices where each set specify the indices
            of a basis. Note len(symbols) == len(indices)

    Example:

    Create a generator for a rocksalt structure with two basis

    >>> from ase.build import bulk
    >>> from clease.montecarlo import RandomFlipWithinBasis
    >>> atoms = bulk("LiO", crystalstructure="rocksalt", a=3.9)*(3, 3, 3)
    >>> basis1 = [a.index for a in atoms if a.symbol == "Li"]
    >>> basis2 = [a.index for a in atoms if a.symbol == "O"]
    >>> generator = RandomFlipWithinBasis([["Li", "X"], ["O", "V"]], atoms, [basis1, basis2])
    """

    CHANGE_NAME = 'flip_within_basis_move'

    def __init__(self,
                 symbols: Sequence[Sequence[str]],
                 atoms: Atoms,
                 indices: Sequence[Sequence[int]] = None,
                 **kwargs):
        super().__init__(**kwargs)

        if len(symbols) != len(indices):
            raise ValueError("Possible symbols must be specified for all basis.")

        if not _symbols_in_basis_are_unique(symbols):
            raise ValueError("Symbols within each basis must be unique")

        if not _index_occur_only_once(indices):
            raise ValueError("Each index can only occur in one basis and only once in each basis.")

        self._flippers = [RandomFlip(s, atoms, i) for s, i in zip(symbols, indices)]

    def get_single_trial_move(self) -> Sequence[SystemChange]:
        """
        Produce a trial move by choosing a random flipper
        """
        flipper = random.choice(self._flippers)
        return flipper.get_single_trial_move()


def _symbols_in_basis_are_unique(nested_seq: Sequence[Sequence[str]]) -> bool:
    """
    Check if all items in the sub-lists are unique.
    """
    for sub in nested_seq:
        if len(sub) != len(set(sub)):
            return False
    return True


def _index_occur_only_once(nested_seq: Sequence[Sequence[int]]) -> bool:
    flattened = flatten(nested_seq)
    return len(flattened) == len(set(flattened))
