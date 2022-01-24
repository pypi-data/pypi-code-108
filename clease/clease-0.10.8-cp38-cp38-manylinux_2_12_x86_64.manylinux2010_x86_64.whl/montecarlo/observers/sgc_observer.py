import numpy as np
from clease.montecarlo.averager import Averager
from .mc_observer import MCObserver


class SGCObserver(MCObserver):
    """
    Observer mainly intended to track additional quantities needed when
    running SGC Monte Carlo. This observer has to be executed on every MC step.

    Parameters:

    calc: `clease.calculators.Clease`
        Clease calculator
    """

    name = "SGCObersver"

    def __init__(self, calc):
        super().__init__()
        self.calc = calc
        E = calc.get_potential_energy()
        n_singlets = len(self.calc.get_singlets())
        self.quantities = {
            "singlets": np.zeros(n_singlets, dtype=np.float64),
            "singlets_sq": np.zeros(n_singlets, dtype=np.float64),
            "energy": Averager(ref_value=E),
            "energy_sq": Averager(ref_value=E**2),
            "singl_eng": np.zeros(n_singlets, dtype=np.float64),
            "counter": 0
        }

    def reset(self):
        """Reset all variables to zero."""
        self.quantities["singlets"][:] = 0.0
        self.quantities["singlets_sq"][:] = 0.0
        self.quantities["energy"].clear()
        self.quantities["energy_sq"].clear()
        self.quantities["singl_eng"][:] = 0.0
        self.quantities["counter"] = 0

    def __call__(self, system_changes):
        """Update all SGC parameters.

        Parameters:

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """
        self.quantities["counter"] += 1
        new_singlets = self.calc.get_singlets()

        E = self.calc.results['energy']

        self.quantities["singlets"] += new_singlets
        self.quantities["singlets_sq"] += new_singlets**2
        self.quantities["energy"] += E
        self.quantities["energy_sq"] += E**2
        self.quantities["singl_eng"] += new_singlets * E

    @property
    def energy(self):
        return self.quantities["energy"]

    @property
    def energy_sq(self):
        return self.quantities["energy_sq"]

    @property
    def singlets(self):
        return self.quantities["singlets"]

    @property
    def singl_eng(self):
        return self.quantities["singl_eng"]

    @property
    def counter(self):
        return self.quantities["counter"]

    def interval_ok(self, interval):
        return interval == 1
