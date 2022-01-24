from typing import Sequence
import numpy as np
from clease.datastructures import SystemChange
from .bias_potential import BiasPotential


class BinnedBiasPotential(BiasPotential):
    """
    Binned bias potential is a bias potential that is sampled on a grid.

    Parameters:

    xmin: float
        Minimum value for the collective variable

    xmax: float
        Maximum value for the collective variable

    nbins: int
        Number of bins

    getter: MCObserver
        Callable object for getting the collective variable.
        It needs to support the peak key word.
    """

    def __init__(self, xmin=0.0, xmax=1.0, nbins=10, getter=None):
        self.xmin = xmin
        self.xmax = xmax
        self.nbins = nbins
        self.values = np.zeros(self.nbins)
        self.dx = (self.xmax - self.xmin) / self.nbins
        self.getter = getter

    def get_index(self, x):
        """Return the index corresponding to an x value."""
        i = int((x - self.xmin) / self.dx)
        if i >= self.nbins:
            i = self.nbins - 1
        elif i < 0:
            i = 0
        return i

    def get_x(self, index):
        """Return x value corresponding to an index."""
        return self.xmin + index * self.dx + 0.5 * self.dx

    def evaluate(self, x):
        """Evaluate the bias potential at x."""
        i = self.get_index(x)
        if i == 0:
            y_left = self.values[0]
            y_right = self.values[1]
            x_left = self.get_x(0)
            y = y_left + (x - x_left) * (y_right - y_left) / self.dx
        elif i == self.nbins - 1:
            y_left = self.values[self.nbins - 2]
            y_right = self.values[self.nbins - 1]
            x_left = self.get_x(self.nbins - 2)
            y = y_left + (x - x_left) * (y_right - y_left) / self.dx
        else:
            x_left = self.get_x(i - 1)
            x_center = x_left + self.dx
            x_right = x_center + self.dx
            y_left = self.values[i - 1]
            y_center = self.values[i]
            y_right = self.values[i + 1]
            fac = 1.0 / self.dx**2

            # Lagrange polynomial
            y = 0.5*fac*(x - x_center)*(x-x_right)*y_left - \
                fac*(x - x_left)*(x - x_right)*y_center + \
                0.5*fac*(x - x_left)*(x-x_center)*y_right
        return y

    def __call__(self, system_changes: Sequence[SystemChange]):
        """Get the bias potential value after the system_change."""
        x = self.getter(system_changes, peak=True)
        return self.evaluate(x)

    def todict(self):
        """Return dictionary representation. (Does not include the getter)"""
        return {
            'xmin': self.xmin,
            'xmax': self.xmax,
            'values': self.values.tolist(),
            'nbins': self.nbins,
            'dx': self.dx
        }

    def from_dict(self, data):
        """Initialize from a dictionary (Does not include the getter)."""
        self.xmin = data['xmin']
        self.xmax = data['xmax']
        self.values = np.array(data['values'])
        self.nbins = data['nbins']
        self.dx = data['dx']

    def calculate_from_scratch(self, atoms):
        """Calculate the value from scratch."""
        x = self.getter.calculate_from_scratch(atoms)
        return self.evaluate(x)

    def local_update(self, x, dE):
        """Perform a local update."""
        i = self.get_index(x)
        self.values[i] += dE

    def zero(self):
        """Set all values to zero."""
        self.values[:] = 0

    def get_coeff(self):
        """Return all values."""
        return self.values
