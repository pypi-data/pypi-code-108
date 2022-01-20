## Interface All Priors Must Implement

import numpy as np

class AbstractPrior:
    """A Prior holds the mean and variance of a prior to use in a particular analysis.
    At the moment, it is always Gaussian.
    Priors may apply various transformations to the original data, and will
    generally include parameters controlling those transformations.

    Returned mean, sd and variance should be numpy arrays with the same dimensions
    as the basis image being fit.

    Currently priors do NOT evaluate the likelihood of any data, though it would be a reasonable
    extension for them to do so.  This likelihood is just the likelihood of the data given the prior,
    not the overall Bayesion likelihood.

    Clients MUST only access these objects via their methods to assure proper caching
    and invalidation behavior when the parameters are changed.  An alternate strategy would be 
    to treat these objects as constant, with a new one created just before each calculation.  Given
    their potentially involved setup, that seems undesirable.
    """

    def distribution(self):
        "Type of distribution I represent"
        return "Gaussian"

    def mean(self):
        "return prior mean"

    def sd(self):
        "return prior standard deviation"

    def var(self):
        "return prior variance"
        s = self.sd()
        return s*s
    
    def name(self):
        "The human-friendly name of this prior"
        return str(type(self))

class AdjustmentPrior(AbstractPrior):
    """Performs some standard adjustments to the prior
        
    basis is, for now, a module, but the key thing is it must implement the 
        ixsc, ixscbanded, linsc, the corresponding bvec_* constants and add_bumps_to_pf.

    bvec - 2D float array specifying intercept and amplitude for parameter
           space functions

    scale - the overall scale of the prior variance
    scale_origin - prior scale at the origin - generally set huge
                           to allow data to determine overall scale
    bumps - dictionary containing set of "bump" filters to implement
    bump_types - set of choices for "bump" filter types to add to k-space
                    paramter function; uses scipy.signal window types 
                    so consult that documentation for available types - 
                    currently only types that only require window type name
                    and size are used - current choices are: 
                    "boxcar"
                    "blackman"
                    "hann"
                    "bartlett"
                    "flattop"
                    "parzen"
                    "bohman"
                    "blackmanharris"
                    "nuttall"
                    "barthann"
    bump_default_type - the default window type used (currently "blackman")

    Subclasses must provide methods
    _markDirty()
    mean() which should call _adjustMean()
    sd()

    And should set the instance variable
    _iorigin
    early on.  It is index of appropriate type and dimension to origin.

    """


    # These are class variables
    # Currently bumps are tied to the basis and only make sense for fourier
    bump_types = ["boxcar","blackman","hann","bartlett","flattop","parzen","bohman","blackmanharris","nuttall","barthann"]
    bump_default_type = "blackman"

    def __init__(self, basis, bvec, scale, scale_origin):
        self._bvec = bvec
        self._scale = scale
        self._scale_origin = scale_origin

        # Create an empty bump dictionary
        # keys are text strings for scipy.signal.window
        # available bump types from scipy.signal.window are 
        # (others like gaussian require more paramters):
        #
        # Due to our use in k-space picking the preferred versions
        # of these, which are the versions that end at 0
        # boxcar - kspace ring filter 
        # triang - pretty self explanatory - XXX - use bartlett instead 
        # blackman - nice decaying tails <- use as default
        # hamming - nice decaying tails - XXX
        # hann - nice decaying tails <- use this instead of hamming
        # bartlett - same as triang but ending at 0
        # flattop - fast decaying to below 0 and back <- should be 2nd def.
        # parzen - nice decaying tails
        # bohman - nice decaying tails
        # blackmanharris - good narrow, decaying tails 
        # nuttall - good narrow, decaying tail
        # barthann - kind of fat tails with pointy top
        #
        # Read about the properties of these at:
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.get_window.html#scipy.signal.windows.get_window
        # functions and values are 3 element arrays containing:
        # 1) the position of the k-space filter in terms
        #    of the fraction of Kx max
        # 2) the amplitude of the k-space filter in terms
        #    of the fraction of parameter function max - bvec[1]
        # 3) the width of the filter to send to the window function
        #    specified in terms of a fraction of Kx max
        self._bumps = {}
        self._bump_type = type(self).bump_default_type
        self._basis = basis

    def _markDirty(self):
        "invalidate all cached values"


    def setbvec(self, bs):
        self._bvec = bs
        self._markDirty()

    def setScale(self, s):
        self._scale = s
        self._markDirty()

    def setScale_origin(self, s):
        self._scale_origin = s
        self._markDirty()

    def setbump_type(self, bt, reset=True):
        "Set a new bump type and empty existing bumps unless reset==False"
        # reset is ignored if bump type is unchanged
        assert bt in bump_types
        if bt != self._bump_type:
            self._bump_type = bt
            if reset:
                self._bumps = {}
            self._markDirty()

    def bvec(self):
        return self._bvec

    def scale(self):
        return self._scale

    def scale_origin(self):
        return self._scale_origin

    def bump_type(self):
        return self._bump_type

    def bumps(self):
        "consider this read only access"
        return self._bumps

    def add_bump(self,my_key,position,amplitude,width):
        """

        adds a bump filter to the self._bumps dictionary

        Inputs:
            my_key - the name of an appropriate scipy.signal shape
            position -  fraction of kmax for location of bump filter
            amplitude - fraction of maximum of parameter function 
                        for amplitudeof of bump filter 
            width -     fraction of kmax for width of bump filter        

        Outputs:
            adds bump filter to self.bumps dictionary

        """
        key_orig = my_key.split(".")[0]
        if my_key in self._bumps:
            isGoodKey = False
            for i in range(10): # No more than ten bump filters of any kind !!!!
                new_key = key_orig+"."+str(i)
                if new_key not in self._bumps:
                    isGoodKey = True
                    break
            if not isGoodKey:
                raise RuntimeError("No more than 10 bump filters of a type allowed.  Exceeded for type "+key_orig)
        else:
            new_key = my_key
        self._bumps[new_key] = np.array([float(position),float(amplitude),float(width)])
        self._markDirty()
        return

    def _adjustMean(self, mean):
        "return mean with all adjustments applied"
        if self._bumps:
            mean += self._basis.add_bumps_to_pf(self._bvec, self._kdist, self._bumps, np.int(np.max(self._kdist)))
        self._mean_init = mean[self._iorigin]
        mean[self._iorigin] = 0.
        return mean

