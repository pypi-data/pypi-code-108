from typing import Union
import logging
from ase import Atoms
from clease.datastructures import SystemChanges
from clease.calculator import Clease

__all__ = ('MCEvaluator', 'CEMCEvaluator', 'construct_evaluator')

logger = logging.getLogger(__name__)


class MCEvaluator:
    """A Montecarlo evaluator class, used to perform the energy evaluations
    within a Montecarlo run.

    Args:
        atoms (ase.Atoms): ASE Atoms object to be used for the evaluation.
            This atoms object may be mutated.
    """

    def __init__(self, atoms: Atoms):
        self._atoms = atoms

    @property
    def atoms(self):
        return self._atoms

    def get_energy(self, applied_changes: SystemChanges = None) -> float:
        """Evaluate the energy of a system.
        If a change is sufficiently local/small, it there, in some situations,
        may be other ways of evaluating the energy than a full calculation.
        Must return the energy of the new configuration.

        The applied changes only reflect what has already been applied to the system.

        Args:
            applied_changes (SystemChanges, optional): A list of changes which has been applied to
                the atoms object. This change has already been applied, and is only for bookkeeping
                purposes, if evaluation schemas want to make decisions based on what has changed.
                Defaults to None.

        Returns:
            float: Energy of the atoms object.
        """
        # pylint: disable=unused-argument
        # system_changes are passed in (optionally) in order to allow for localized evaluations
        # See discussion:
        # https://gitlab.com/computationalmaterials/clease/-/issues/268
        return self.atoms.get_potential_energy()

    def reset(self) -> None:
        """Perform a reset on the evaluator and/or on the atoms"""

    def apply_system_changes(self, system_changes: SystemChanges, keep=False) -> None:
        """Mutate the atoms object to reflect the system change.

        Args:
            system_changes (SystemChanges): Sequence of changes to be applied.
            keep (bool, optional): Whether to call
                :meth:`~clease.montecarlo.mc_evaluator.MCEvaluator.keep_system_changes`
                after applying changes. Defaults to False.
        """
        for change in system_changes:
            change.apply_change(self.atoms)
        if keep:
            self.keep_system_changes(system_changes=system_changes)

    def undo_system_changes(self, system_changes: SystemChanges) -> None:
        """Mutate the atoms object to undo the system change.

        Args:
            atoms (Atoms): Atoms object to be mutated.
            system_changes (SystemChanges): Sequence of changes to be applied.
        """
        for change in system_changes:
            change.undo_change(self.atoms)

    def keep_system_changes(self, system_changes: SystemChanges = None) -> None:
        """A set of system changes are to be kept. Perform necessary actions to prepare
        for a new evaluation."""

    def get_energy_given_change(self, system_changes: SystemChanges) -> float:
        """Calculate the energy of a set of changes, and undo any changes.

        Args:
            atoms (Atoms): Atoms object to be mutated.
            system_changes (SystemChanges): Sequence of changes to be applied.

        Returns:
            float: The resulting energy from a
            call to :meth:`~clease.montecarlo.mc_evaluator.MCEvaluator.get_energy`.
        """
        self.apply_system_changes(system_changes)
        energy = self.get_energy(applied_changes=system_changes)
        self.undo_system_changes(system_changes)
        return energy

    def synchronize(self) -> None:
        """Ensure the calculator and atoms objects are synchronized."""


class CEMCEvaluator(MCEvaluator):
    """MC Evaluator to be used with the CLEASE CE Calculator.
    Assumes the attached calculator is a Clease Calculator"""

    def __init__(self, atoms: Atoms):
        if not isinstance(atoms.calc, Clease):
            raise ValueError("Clease calculator must be attached to the atoms object "
                             "when using CEMCEvaluator")
        super().__init__(atoms)

    def get_energy(self, applied_changes: SystemChanges = None) -> float:
        return self.atoms.calc.get_energy()

    def reset(self) -> None:
        """Perform a reset on the evaluator and/or on the atoms"""
        self.atoms.calc.clear_history()
        super().reset()

    def apply_system_changes(self, system_changes: SystemChanges, keep=False) -> None:
        """Mutate the atoms object to reflect the system change.

        Args:
            atoms (Atoms): Atoms object to be mutated.
            system_changes (SystemChanges): Sequence of changes to be applied.
            keep (bool, optional): Whether to call
                :meth:`~clease.montecarlo.mc_evaluator.MCEvaluator.keep_system_changes`
                after applying changes. Defaults to False.
        """
        atoms = self.atoms
        atoms.calc.apply_system_changes(system_changes)
        if keep:
            self.keep_system_changes(system_changes=system_changes)

    def undo_system_changes(self, system_changes: SystemChanges) -> None:
        """Mutate the atoms object to undo the system change.

        Args:
            atoms (Atoms): Atoms object to be mutated.
            system_changes (SystemChanges): Sequence of changes to be applied.
        """
        self.atoms.calc.undo_system_changes()

    def keep_system_changes(self, system_changes: SystemChanges = None) -> None:
        """A set of system changes are to be kept. Perform necessary actions to prepare
        for a new evaluation."""
        self.atoms.calc.keep_system_changes()

    def get_energy_given_change(self, system_changes: SystemChanges) -> float:
        """Calculate the energy of a set of changes, and undo any changes.

        Args:
            atoms (Atoms): Atoms object to be mutated.
            system_changes (SystemChanges): Sequence of changes to be applied.

        Returns:
            float: The resulting energy from a
            call to :meth:`~clease.montecarlo.mc_evaluator.MCEvaluator.get_energy`.
        """
        return self.atoms.calc.get_energy_given_change(system_changes)

    def synchronize(self) -> None:
        """Ensure the calculator and atoms objects are synchronized."""
        # Recalculate the CF
        self.atoms.calc.update_cf()


def _make_mc_evaluator_from_atoms(atoms: Atoms) -> MCEvaluator:
    """Construct a new MC Evaluator based on the calculator object attached to the Atoms object.

    Raises a ``RuntimeError`` is the Atoms object has no calculator."""
    calc = atoms.calc
    if calc is None:
        raise RuntimeError('Atoms object must have a calculator object.')
    if isinstance(calc, Clease):
        # Return the MC Evaluator specialized for the CLEASE calculator
        logger.debug('Constructed a new CE MC Evaluator.')
        return CEMCEvaluator(atoms)
    # Return the generic MC Evaluator
    logger.debug('Constructed a generic MC Evaluator.')
    return MCEvaluator(atoms)


def construct_evaluator(system: Union[Atoms, MCEvaluator]) -> MCEvaluator:
    """Helper function for constructing a new evaluator object, either by passing
    in an ASE atoms object or an explicit evaluator object.

    Args:
        system (Union[Atoms, MCEvaluator]): If the system is an Atoms object,
            then a new :class:`~clease.montecarlo.mc_evaluator.MCEvaluator`
            object is created on the basis of the attached calculator.
            Otherwise, if the system is already an Evaluator object,
            the same object is returned.

    Raises:
        TypeError: If the system is not either an ASE atoms object
            or an ``MCEvaluator``.

    Returns:
        MCEvaluator: The evaluator object to be used.
    """

    if isinstance(system, Atoms):
        # Construct the default evaluator object
        logger.debug('Creating a new default evaluator.')
        return _make_mc_evaluator_from_atoms(system)
    if isinstance(system, MCEvaluator):
        # User supplied a custom evaluator
        logger.debug('Using a user-defined evaluator: %s', system)
        return system
    raise TypeError(f'Received an unknown system: {system}')
