import logging
import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator
from .mc_observer import MCObserver

logger = logging.getLogger(__name__)


class LowestEnergyStructure(MCObserver):
    """Track the lowest energy state visited during an MC run.

    atoms: Atoms object
        Atoms object used in Monte Carlo

    verbose: bool
        If `True`, progress messages will be printed
    """

    name = "LowestEnergyStructure"

    def __init__(self, atoms, verbose=False):
        super().__init__()
        self.atoms = atoms
        self.lowest_energy = np.inf
        self.lowest_energy_cf = None
        self.emin_atoms = None
        self.verbose = verbose

    def reset(self):
        self.lowest_energy = np.inf
        self.lowest_energy_cf = None
        self.emin_atoms = None

    @property
    def calc(self):
        return self.atoms.calc

    @property
    def energy(self):
        return self.calc.results['energy']

    def __call__(self, system_changes):
        """
        Check if the current state has lower energy and store the current
        state if it has a lower energy than the previous state.

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """

        if self.emin_atoms is None or self.energy < self.lowest_energy:
            self._update_emin()
            dE = self.energy - self.lowest_energy
            msg = "Found new low energy structure. "
            msg += f"New energy: {self.lowest_energy} eV. Change: {dE} eV"
            logger.info(msg)
            if self.verbose:
                print(msg)

    def _update_emin(self):
        self.lowest_energy_cf = self.calc.get_cf()
        self.lowest_energy = self.energy

        # Store emin atoms, and attach a cache calculator
        self.emin_atoms = self.atoms.copy()
        calc_cache = SinglePointCalculator(self.emin_atoms, energy=self.energy)
        self.emin_atoms.calc = calc_cache
