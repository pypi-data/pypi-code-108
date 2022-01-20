# Use some functional form to simplify the prior
from bifs.priors.AbstractPrior import *

def param_func_choices():
    return ["Inverse Power Decay", "Banded Inverse Power Decay", "Linear Decay"]

class FunctionalPrior(AdjustmentPrior):
    """ Abstract class with common logic for all functional priors
    kdist is an array with distance from center of Fourier space but shifted so origin is at [0], [0,0] or [0,0,0]
            as appropriate for image dimension
    _iorgin holds a tuple with the origin index once dimensionality is set

    See AdjustmentPrior for other variables.

    Note that it is very important to do all setup of the mean before touching the sd.
    The only setters of the mean are internal to the class, but remember the sd depends on the mean.
    """
    def __init__(self, basis, kdist, bvec, scale = 0.0005, scale_origin = 10.**7):
        super().__init__(basis, bvec, scale, scale_origin)
        self.setkdist(kdist)
        # setkdist calls _markDirty

    def _markDirty(self):
        super()._markDirty()
        # see https://hynek.me/articles/hasattr/ for some reasons not to use hasattr for testing if a variable is present
        # Also https://stackoverflow.com/questions/24971061/python-hasattr-vs-getattr
        # So instead we set to None
        self._mean = None
        self._sd = None
        self._var = None

    def setkdist(self, kdist):
        self._kdist = kdist
        self._iorigin = tuple(0 for x in range(len(kdist.shape)))
        self._markDirty()

    def mean(self):
        if self._mean is None:
            self._mean = self._compute_mean()
        return self._mean

    def sd(self):
        if self._sd is None:
            self._sd = self._compute_sd()
        return self._sd

    def _compute_sd(self):
        """all functional forms currently share this scaling,
        which implies a strong prior"""
        sd = self.mean()*self._scale
        sd[self._iorigin] = self._scale_origin
        return sd

    def var(self):
        # it might be faster not to cache this at all
        if self._var is None:
            s = self.sd()
            self._var = s*s
        return self._var

class InversePowerDecayPrior(FunctionalPrior):
    """
    decay - float decay exponent for the inverse power paramter function
    """
    def __init__(self, basis, kdist, bvec = None, scale = 0.0005, scale_origin = 10.**7, decay = 0.5):
        if bvec is None:
            bvec = basis.bvec_ixsc
        super().__init__(basis, kdist, bvec, scale, scale_origin)
        self._decay = decay

    def name(self):
        return "Inverse Power Decay"

    def setdecay(self, decay):
        if decay != self.decay:
            self._decay = decay
            self._markDirty()

    def decay(self):
        return self._decay

    def _compute_mean(self):
        mean = self._basis.ixsc(self._bvec, self._kdist, self._decay)
        return self._adjustMean(mean)

class BandedInversePowerDecayPrior(InversePowerDecayPrior):
    """
    banded_cutoff - cutoff for banded inverse power k-space paramter function 
    """
    def __init__(self, basis, kdist, bvec = None, scale = 0.0005, scale_origin = 10.**7, decay = 0.5, banded_cutoff=50.):
        if bvec is None:
            bvec = basis.bvec_ixscbanded
        super().__init__(basis, kdist, bvec, scale, scale_origin, decay)
        self._banded_cutoff = banded_cutoff

    def name(self):
        return "Banded Inverse Power Decay"

    def setbanded_cutoff(self, bc):
        self._banded_cutoff = bc
        self._markDirty()

    def banded_cutoff(self):
        return self._banded_cutoff

    def _compute_mean(self):
        mean = self._basis.ixscbanded(self._bvec, self._kdist, self._decay, self._banded_cutoff)
        return self._adjustMean(mean)

class LinearDecayPrior(FunctionalPrior):
    """Simple linear decay.
    """
    def __init__(self, basis, kdist, bvec = None, scale = 0.0005, scale_origin = 10.**7):
        if bvec is None:
            bvec = basis.bvec_linsc
        super().__init__(basis, kdist, bvec, scale, scale_origin)

    def name(self):
        return "Linear Decay"

    def _compute_mean(self):
        mean = self._basis.linsc(self._bvec, self._kdist)
        return self._adjustMean(mean)