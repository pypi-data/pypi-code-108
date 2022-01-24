from .mc_observer import MCObserver


class ConcentrationObserver(MCObserver):
    """
    Observer that can be attached to a MC run, to track the concenctration of a
    particular element. This observer has to be executed on every MC step.

    Parameters:

    atoms: Atoms object
        Atoms object used for MC

    element: str
        The element that should be tracked
    """

    name = "ConcentrationObserver"

    def __init__(self, atoms, element=None):
        super().__init__()
        self.element = element
        self.n = len(atoms)
        self.init_conc = self.calculate_from_scratch(atoms)
        self.current_conc = self.init_conc
        self.avg_conc = self.current_conc
        self.avg_conc_sq = self.current_conc**2
        self.num_calls = 1

    def new_concentration(self, system_change):
        """Calculate the new consentration after the changes."""
        new_conc = self.current_conc
        for change in system_change:
            if change[2] == self.element:
                new_conc += 1.0 / self.n
            if change[1] == self.element:
                new_conc -= 1.0 / self.n
        return new_conc

    def __call__(self, system_change, peak=False):
        if system_change is None:
            return self.current_conc

        new_conc = self.new_concentration(system_change)

        if peak:
            return new_conc

        self.current_conc = new_conc
        self.avg_conc += self.current_conc
        self.avg_conc_sq += self.current_conc**2
        self.num_calls += 1
        return self.current_conc

    def reset(self):
        """Reset the averages."""
        self.avg_conc = self.current_conc
        self.avg_conc_sq = self.current_conc**2
        self.num_calls = 1

    def get_averages(self):
        mean_conc = self.avg_conc / self.num_calls
        var_conc = self.avg_conc_sq / self.num_calls - mean_conc**2
        return {f"conc_{self.element}": mean_conc, f"conc_var_{self.element}": var_conc}

    def calculate_from_scratch(self, atoms):
        num_atoms = sum(1 for a in atoms if a.symbol == self.element)
        return num_atoms / len(atoms)

    def interval_ok(self, interval):
        return interval == 1
