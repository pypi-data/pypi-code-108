import numpy as np
from .mc_observer import MCObserver


class DiffractionUpdater:
    """
    Utility class for all objects that require tracing of Fourier reflection.
    See docstring of DiffractionObserver for explanation of the arguments.
    This observer has to be executed on every MC step.
    """

    def __init__(self, atoms=None, k_vector=(), active_symbols=(), all_symbols=()):
        self.orig_symbols = [atom.symbol for atom in atoms]
        self.k_vector = k_vector
        self.N = len(atoms)
        self.k_dot_r = atoms.get_positions().dot(self.k_vector)
        self.indicator = {k: 0 for k in all_symbols}
        for symb in active_symbols:
            self.indicator[symb] = 1.0

        self.value = self.calculate_from_scratch(self.orig_symbols)
        self.prev_value = self.value

    def update(self, system_changes):
        """Update the reflection value."""
        self.prev_value = self.value
        for change in system_changes:
            f_val = np.exp(1j * self.k_dot_r[change[0]]) / self.N
            self.value += self.indicator[change[2]] * f_val
            self.value -= self.indicator[change[1]] * f_val

    def undo(self):
        """Undo the last update."""
        self.value = self.prev_value

    def reset(self):
        """Reset all values."""
        self.value = self.calculate_from_scratch(self.orig_symbols)
        self.prev_value = self.value

    def calculate_from_scratch(self, symbols):
        """Calculate the intensity from sctrach."""
        value = 0.0 + 1j * 0.0
        for i, symb in enumerate(symbols):
            value += self.indicator[symb] * np.exp(1j * self.k_dot_r[i])
        return value / len(symbols)


class DiffractionObserver(MCObserver):
    """
    Trace the reflection intensity.

    Parameters:

    atoms: Atoms
        Atoms object used in Monte Carlo

    k_vector: list
        Fourier reflection to be traced

    active_symbols: list
        List of symbols that reflects

    all_symbols: list
        List of all symbols in the simulation

    name: str
        Name of the DiffractionObserver
        (users are given the freedom to set names because they can attach
        multiple DiffractionObserver instances)


    Example:

    Consider a system where Al, Mg and Si occupy FCC lattice sites. We want to
    trace the occurence of Mg layers that are separated by a distance 3*a
    where *a* is the lattice parameter. We further assume that the *y*-axis is
    normal to the planes we want to trace. In that case, we specify the
    variables as

    >>> from ase.build import bulk
    >>> import numpy as np
    >>> a = 4.05
    >>> atoms = bulk('Al', crystalstructure='fcc', a=a)
    >>> k_vector = [0, 2.0*np.pi/(3*a), 0]
    >>> active_elements = ['Mg']
    >>> all_symbols = ['Al', 'Mg', 'Si']

    If we do not wish to distinguish Mi and Si (we do not distiguish Mg layer,
    Si layer or a mixture of the two) the `active_elements` is changed to

    >>> active_elements = ['Mg', 'Si']
    """

    def __init__(self,
                 atoms=None,
                 k_vector=(),
                 active_symbols=(),
                 all_symbols=(),
                 name="reflection1"):
        super().__init__()
        self.updater = \
            DiffractionUpdater(atoms=atoms, k_vector=k_vector,
                               active_symbols=active_symbols,
                               all_symbols=all_symbols)
        self.avg = self.updater.value
        self.num_updates = 1
        self.name = name

    def __call__(self, system_changes):
        self.updater.update(system_changes)
        self.avg += self.updater.value

    def get_averages(self):
        return {self.name: np.abs(self.avg / self.num_updates)}

    def reset(self):
        self.updater.reset()
        self.avg = self.updater.value
        self.num_updates = 1

    def interval_ok(self, interval):
        return interval == 1
