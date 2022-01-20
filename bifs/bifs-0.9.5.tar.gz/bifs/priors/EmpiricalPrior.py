# Prior based on empirical distribution of data

from bifs.priors.AbstractPrior import *

class EmpiricalPrior(AdjustmentPrior):
    """Empirical Prior
    Since this is an AdjustmentPrior one can add bumps to it.
    The interpretation of scale is different than for FunctionalPriors; here
    it is a multiplicative factor on the empirical sd.
    """
    def __init__(self, data,  basis, bvec, scale=1.0, scale_origin=10.**7):
        """initialize self with data and optional scale.
        data["mean"] is a numpy array
        data["sd"] is a numpy array
        scale will be multiplied by the sd to get the final value
        Note that scale_origin continues to be used as is, without multiplication
        """
        super().__init__(basis, bvec, scale, scale_origin)
        self._emean = data["mean"]
        self._esd = data["sd"]
        self._iorigin = tuple(0 for x in range(len(self._emean.shape)))
        
        # Assure all caches exist
        self._markDirty()

    def name(self):
        return "Empirical"

    def mean(self):
        if self._mean is None:
            self._mean = self._compute_mean()
        return self._mean

    def sd(self):
        if self._sd is None:
            self._sd = self._compute_sd()
        return self._sd

    def _compute_mean(self):
        mean = self._emean
        return self._adjustMean(mean)

    def _compute_sd(self):
        sd = self._esd*self._scale
        sd[self._iorigin] = self._scale_origin
        return sd

    def var(self):
        # it might be faster not to cache this at all
        if self._var is None:
            s = self.sd()
            self._var = s*s
        return self._var

    def _markDirty(self):
        super()._markDirty()
        self._mean = None
        self._sd = None
        self._var = None