import logging
import numpy as np
from clease.tools import add_file_extension
from .mc_observer import MCObserver

logger = logging.getLogger(__name__)


class EnergyEvolution(MCObserver):
    """Trace the evolution of energy."""

    name = "EnergyEvolution"

    def __init__(self, mc, ignore_reset=False):
        super().__init__()
        self.mc = mc
        self.energies = []
        self.mean_energies = []
        self.ignore_reset = ignore_reset

    def __call__(self, system_changes):
        """Append the current energy to the MC object.

        Parameters:

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """
        self.energies.append(self.mc.current_energy)
        self.mean_energies.append(self.mc.mean_energy.mean)

    def reset(self):
        """Reset the history."""
        if self.ignore_reset:
            return
        self.energies = []

    def save(self, fname: str = "energy_evolution.csv") -> None:
        """Save the energy evolution in .csv file.

        :param fname: File name of .csv file. Adds extension if none is given.
        """
        full_fname = add_file_extension(fname, '.csv')
        np.savetxt(full_fname, self.energies, delimiter=",")
        logger.info("Energy evolution data saved to %s.", full_fname)
