from .mc_observer import MCObserver


class CorrelationFunctionObserver(MCObserver):
    """Track the history of the correlation function.

    Parameters:

    calc: `clease.calculators.Clease`
        Clease calculator

    names: list
        List with correlation functions to track.
        If None, all correlation functions are tracked.
    """
    name = "CorrelationFunctionObserver"

    def __init__(self, calc, names=None):
        super().__init__()
        current_cf = calc.get_cf()
        self.names = names
        if names is None:
            self.names = list(current_cf.keys())
        self.cf = {x: current_cf[x] for x in self.names}
        self.calc = calc
        self.counter = 1

    def __call__(self, system_changes):
        """Update the correlation functions.

        Parameters:

        system_changes: list
            System changes. See doc-string of
            `clease.montecarlo.observers.MCObserver`
        """
        new_cf = self.calc.get_cf()
        for name in self.names:
            self.cf[name] += new_cf[name]
        self.counter += 1

    def reset(self):
        self.cf = self.calc.get_cf()
        self.counter = 1

    def get_averages(self):
        return {'cf_' + k: v / self.counter for k, v in self.cf.items()}
