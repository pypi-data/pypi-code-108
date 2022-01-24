from typing import Sequence
import numpy as np
from clease.datastructures import SystemChange
from .bias_potential import BiasPotential


# pylint: disable=too-many-instance-attributes
class GaussianKernelBiasPotential(BiasPotential):
    """
    Bias potential represented by a sum of Gaussian kernels.

    Parameters:

        xmin: float
            Minimum coordinate value

        xmax: float
            Maximum coordinate value

        num_kernels: int
            Number of Gaussian kernels

        width: float
            Width of the kernel (=exp(-(x/width)**2)

        getter: MCObserver
            Observer that can return the coordinate value after a given MC step.
            There are two requirements for the observer in addition to being a
            subclass of MCObsers.
            1. It needs to support None as an argument for the system changes.
            In that case, the code expects that the current value of the
            coordinate is returned
            2. It needs to support peak=True/False keyword. If peak=True,
            the code expects to get the coordinate after the change,
            but the observer should not update its current value.
    """

    def __init__(self, xmin=0.0, xmax=1.0, num_kernels=10, width=0.1, getter=None):

        self.xmin = xmin
        self.xmax = xmax
        self.width = width
        self.getter = getter
        self.limit = 0.01

        self.pad = int(np.sqrt(-np.log(self.limit)) + 1)
        self.num_kernels = num_kernels + 2 * self.pad
        self.coeff = np.zeros(self.num_kernels)
        self.xmin_corrected = self.xmin - self.pad * width
        self.xmax_corrected = self.xmax + self.pad * width
        self.centers = np.linspace(self.xmin_corrected, self.xmax_corrected, self.num_kernels)
        self.dx = (self.xmax_corrected - self.xmin_corrected) / \
            (self.num_kernels-1)

    def get_index(self, x):
        return int((x - self.xmin_corrected) / self.dx)

    def get_x(self, indx):
        return self.xmin_corrected + self.dx * indx

    def inside_range(self, x):
        """
        Return the indices of the gaussians that are that has a contribution of
        more than 0.01 at position x

        Parameters
            x: float
                Position to be evaluated

        Returns: int, int
            lower index, upper index
        """
        delta = self.width * np.sqrt(-np.log(self.limit))
        upper = x + delta
        lower = x - delta
        i_upper = self.get_index(upper)
        i_lower = self.get_index(lower)
        assert i_lower >= 0
        assert i_upper < self.num_kernels
        return i_lower, i_upper

    def _gaussian(self, x, x0):
        return np.exp(-((x - x0) / self.width)**2)

    def evaluate(self, x):
        low, high = self.inside_range(x)
        w = self._gaussian(x, self.centers[low:high + 1])
        return np.sum(self.coeff[low:high + 1] * w)

    def __call__(self, system_changes: Sequence[SystemChange]):
        x = self.getter(system_changes, peak=True)
        return self.evaluate(x)

    def local_update(self, x, dE):
        """Increase the local energy at x by an amount dE."""
        low, high = self.inside_range(x)
        w = self._gaussian(x, self.centers[low:high + 1])

        # Update the coefficient in such a way that the value at
        # point x is increased by dE and that the L2 norm of the
        # change in coefficient is minimised
        self.coeff[low:high + 1] += dE * w / np.sum(w**2)

    def slope(self, x):
        """Evaluate slope."""
        low, high = self.inside_range(x)
        w = self._gaussian(x, self.centers[low:high + 1])
        w *= -(x - self.centers[low:high + 1]) / self.width**2
        return np.sum(self.coeff[low:high + 1] * w)

    def ensure_zero_slope(self, x):
        """Change the coefficients such that the slope is zero at x."""
        low, high = self.inside_range(x)
        c = self.centers[low:high + 1]
        w = self._gaussian(x, self.centers[low:high + 1])
        denom = (w * (x - c) / self.width**2)**2
        lamb = self.slope(x) / np.sum(denom)
        self.coeff[low:high + 1] += lamb * (x - c) * w / self.width**2

    def todict(self):
        return {
            'xmin': self.xmin,
            'xmax': self.xmax,
            'num_kernels': self.num_kernels,
            'width': self.width,
            'coeff': self.coeff.tolist(),
            'centers': self.centers.tolist(),
            'dx': self.dx,
            'xmin_corrected': self.xmin_corrected,
            'xmax_corrected': self.xmax_corrected,
            'pad': self.pad
        }

    def from_dict(self, data):
        self.xmin = data['xmin']
        self.xmax = data['xmax']
        self.num_kernels = data['num_kernels']
        self.width = data['width']
        self.coeff = np.array(data['coeff'])
        self.centers = np.array(data['centers'])
        self.dx = data['dx']
        self.xmin_corrected = data['xmin_corrected']
        self.xmax_corrected = data['xmax_corrected']
        self.pad = data.get('pad', 3)

    def calculate_from_scratch(self, atoms):
        x = self.getter.calculate_from_scratch(atoms)
        return self.evaluate(x)

    def zero(self):
        self.coeff[:] = 0.0

    def get_coeff(self):
        return self.coeff
