from typing import List, Tuple, Sequence, Union
import warnings
import logging
import time
import random
from ase import Atoms
from ase.units import kB
import numpy as np
from clease.datastructures import SystemChange
from .mc_evaluator import MCEvaluator
from .base import BaseMC
from .barrier_models import BarrierModel
from .kmc_events import KMCEventType
from .observers import MCObserver

__all__ = ('KineticMonteCarlo',)

logger = logging.getLogger(__name__)


class KineticMonteCarlo(BaseMC):
    """
    Kinetic Monte Carlo using the residence time algorithm, which is a
    rejection free algorithm and is thus also efficient at low temperatures.

    References:

    [1] Bortz, Alfred B., Malvin H. Kalos, and Joel L. Lebowitz.
        "A new algorithm for Monte Carlo simulation of Ising spin systems."
        Journal of Computational Physics 17.1 (1975): 10-18.

    [2] Rautiainen, T. T., and A. P. Sutton.
        "Influence of the atomic diffusion mechanism on morphologies,
        kinetics, and the mechanisms of coarsening during phase separation."
        Physical Review B 59.21 (1999): 13681.


    :param system: Either an ASE Atoms object
        with an attached calculator, or a pre-initialized
        :ckass:`~clease.montecarlo.mc_evaluator.MCEvaluator`
        object.
    :param barrier: Model used to evaluate the barriers
    :param events: List of KMCEvents used to produce possible events
    :param evaluator: MCEvaluator object, used for customizing how to evaluate
        the energies during an MC run.
    """

    def __init__(self, system: Union[Atoms, MCEvaluator], T: float, barrier: BarrierModel,
                 event_types: Sequence[KMCEventType]):
        super().__init__(system)
        self.T = T
        self.barrier = barrier
        self.event_types = event_types
        self.time = 0.0
        self.attempt_freq = 1e4
        self.observers = []
        self.log_interval = 30
        self.epr = None

    def reset(self):
        """
        Reset the KMC class. All information stored as attributes of KMC and
        in observers will be cleared.
        """
        self.time = 0.0
        for _, obs in self.observers:
            obs.reset()

        if self.epr is not None:
            self.epr.reset()

    @property
    def kT(self) -> float:
        return kB * self.T

    def _update_epr(self, current: int, choice: int, swaps: List[int], cum_rates: np.ndarray):
        """
        Update the EPR tracker (if set).

        :param current: Current position of the vacancy
        :param choice: Chosen index in the cum_rates array
        :param swaps: List of possible swaps
        :param cum_rates: Cummulative transition rates
        """
        if self.epr is None:
            return
        self.epr.update(current, choice, cum_rates, swaps)

    def attach(self, obs: MCObserver, interval: int = 1):
        """
        Attach an observer to the MC run

        :param obs: Instance of MCObserver
        :param interval: Number of steps between each time the observer
            is executed.
        """
        self.observers.append((interval, obs))

    def _rates(self, vac_idx: int) -> Tuple[List[int], np.ndarray]:
        """
        Return the rates for all possible swaps for a vacancy
        at position vac_idx

        :param vac_idx: Position of the vacancy
        """
        swaps = [
            swap for event in self.event_types for swap in event.get_swaps(self.atoms, vac_idx)
        ]
        if len(swaps) == 0:
            raise RuntimeError("No swaps are possible.")
        rates = np.array([self._get_rate_from_swap(swap, vac_idx) for swap in swaps])
        return swaps, rates

    def _get_rate_from_swap(self, swap_idx: int, vac_idx: int) -> float:
        symb = self.atoms[swap_idx].symbol
        system_change = [
            SystemChange(index=vac_idx, old_symb='X', new_symb=symb, name='kmc_swap'),
            SystemChange(index=swap_idx, old_symb=symb, new_symb='X', name='kmc_swap')
        ]
        Ea = self.barrier(self.evaluator, system_change)
        rate = self.attempt_freq * np.exp(-Ea / self.kT)
        if rate < 0.0:
            warnings.warn("Negative rate encountered!")
            rate = 0.001
        return rate

    def _mc_step(self, vac_idx: int, step_no: int) -> int:
        """
        Perform an MC step and return the new index of the moving vacancy

        :param vac_idx: Current position of the vacancy
        :param step_no: Step number
        """
        swaps, rates = self._rates(vac_idx)
        tau = 1.0 / np.sum(rates)
        rates *= tau
        cumulative_rates = np.cumsum(rates)

        rnd = random.random()

        # Argmax returns the first occurence of True
        cum_indx = np.argmax(cumulative_rates > rnd)
        choice = swaps[cum_indx]
        self._update_epr(vac_idx, cum_indx, swaps, cumulative_rates)

        # Apply step
        symb = self.atoms[choice].symbol
        system_change = [
            SystemChange(index=vac_idx, old_symb='X', new_symb=symb, name='kmc_swap'),
            SystemChange(index=choice, old_symb=symb, new_symb='X', name='kmc_swap')
        ]

        # Trigger update, apply changes to the system
        self.evaluator.apply_system_changes(system_change, keep=True)

        self.time += tau

        for interval, obs in self.observers:
            if step_no % interval == 0:
                obs(system_change)
        return choice

    def run(self, num_steps: int, vac_idx: int):
        """
        Run a given number of MC steps. The algorithm uses only
        one vacancy that moves around. Note that there can be more
        vacancies in the system, but they are just treated as regular
        atoms.

        :param num_steps: Number of steps to perform
        :param vac_idx: Index where the moving vacancy is located
        """

        if self.atoms[vac_idx].symbol != 'X':
            raise ValueError(f"Index {vac_idx} is not a vacancy. "
                             f"Symbol: {self.atoms[vac_idx].symbol}")

        # Ensure evaluator is in sync and up-to-date
        # for the CE calculator: make sure that CFs are in sync
        self.evaluator.get_energy()
        self.evaluator.reset()

        now = time.time()
        for i in range(num_steps):
            if self.log_interval is not False and time.time() - now > self.log_interval:
                logger.info("Step %d of %d", i, num_steps)
                now = time.time()
            vac_idx = self._mc_step(vac_idx, i)

        # If entropy is tracked: Flush the buffer
        if self.epr is not None:
            self.epr.flush_buffer()
