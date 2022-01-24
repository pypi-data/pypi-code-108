from typing import Dict, Union
from abc import ABC, abstractmethod
from ase import Atoms
from clease.datastructures import SystemChanges
from clease.montecarlo.mc_evaluator import MCEvaluator, construct_evaluator

__all__ = ('BarrierModel', 'BEPBarrier')


class BarrierModel(ABC):
    """
    Base barrier model class
    """

    def __call__(self, system: Union[Atoms, MCEvaluator], system_changes: SystemChanges) -> float:
        """Get the height of the barrier"""
        # Ensure we have a valid evaluator object
        evaluator = construct_evaluator(system)

        return self.evaluate_barrier(evaluator, system_changes)

    @abstractmethod
    def evaluate_barrier(self, evaluator: MCEvaluator, system_changes: SystemChanges) -> float:
        """Evaluate the height of the barrier"""


class BEPBarrier(BarrierModel):
    """
    BEP barrier implements the Bell-Evans-Polanyi model. It is a simple barrier
    model where the barrier is modelled by the dilute barrier, corrected by
    the change in total energy before and after the jump.

    E_a = Q_s + alpha*(E_2 - E_1)

    where E_1 is the total energy of starting configuration and E_2 is the
    total energy of the end configuration. Q_s is a constant that depends
    on the species. If an isolated solute is diffusing in a host material
    E_1 = E_2. Thus, Q_s represents the barrier of an isolated solute. References:

    1. The `Bell-Evans-Polanyi`_ principle.
    2. Andersen, M., Panosetti, C. and Reuter, K., 2019.
       A practical guide to surface kinetic Monte Carlo simulations.
       Frontiers in chemistry, 7, p.202. DOI: https://doi.org/10.3389/fchem.2019.00202

    :param dilute_barrier: Dictionary representing the dilute barrier for
        each species. Example {'Al': 0.05, 'Mg': 0.03}
    :param alpha: Scalar quantity between 0 and 1 that characterises the position
        of the transition state along the reaction coordinate. Default is 0.5.
        Note as alpha is the same for all jumps, it must be viewed as
        controlling the average barrier position.

    .. _Bell-Evans-Polanyi:
        https://en.wikipedia.org/wiki/Bell%E2%80%93Evans%E2%80%93Polanyi_principle>
    """

    def __init__(
        self,
        dilute_barrier: Dict[str, float],
        alpha: float = 0.5,
    ):
        super().__init__()
        self.dilute_barrier = dilute_barrier
        self.alpha = alpha

    def evaluate_barrier(self, evaluator: MCEvaluator, system_changes: SystemChanges) -> float:
        E1 = evaluator.get_energy()
        # Get the energy given a change, remember to undo the changes again.
        E2 = evaluator.get_energy_given_change(system_changes)

        # Extract the jumping species. The system change should involve
        # a vacancy and another element. Thus, the jumping species is the
        # symbol in system_change that is not a vacancy
        old_symb, new_symb = system_changes[0].old_symb, system_changes[0].new_symb

        # Confirm that one of the symbols is a vacancy
        assert old_symb == 'X' or new_symb == 'X'

        jumping_symb = old_symb if old_symb != 'X' else new_symb
        Ea = self.dilute_barrier[jumping_symb] + self.alpha * (E2 - E1)
        return Ea
