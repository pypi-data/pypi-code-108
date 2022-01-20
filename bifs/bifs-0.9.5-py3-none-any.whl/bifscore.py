
###                        BIFS class                   ### 
###                                                     ###
###         Class for performing Bayesian Image         ###
###         Restoration in Fourier Space (BIFS)         ###

## The filename is bifscore, not bifs or BIFS to avoid trouble
## with the import machinery.  In particular, import bifs, at
## least when executed in this directory, could import bifs.py 
## (old name for this file) rather than the package.  And thus
## from bifs.priors would fail with an error that bifs was not 
## a package.

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from pylab import *
import multiprocessing as mp
from scipy import stats
import imageio
from scipy.optimize import minimize_scalar as ms
from multiprocessing import Pool, TimeoutError
from datetime import datetime
import jsonpickle as jsp
from bifs.priors import FunctionalPrior as FP
from bifs.priors import EmpiricalPrior as EP
from bifs.bifsexception import *

from PyQt5.QtCore import QObject, Signal

import copy

class BIFS(QObject):
    """
    Class BIFS for performing Bayesian image analysis
    in fourier space

    Variables
    ---------

    In the next group, clients should always use the accessor functions listed:

    init_image() - initial loaded image
    k_image() - initial k-space image
    mod_image() - initial modulus image in k-space
    phase_image() - initial phase image in k-space
    bifsk_image() - final BIFS modulus image in k-space
    final_image() - final reconstructed image in image space

    NOTE: We're keeping all these images in the BIFS object for
    now re. testing and experimentation - might be useful to 
    eventually have production run options that are more
    parsimonius re. storage.

    image_file_loaded - whether an image is loaded (True,False)
    initial_image_file_name - file name of initial image
    imdim - int image dimension (1,2 or 3)

    kdist() = distance on the shifted k-space lattice

    view3Dslice - for 3D data this is a 2D array [a,b] where:
                  a = axis perpindicular to slice
                  b = fraction of maximum along that direction 
                      for slice location
    
    prior - string specifying prior distribution to use
            current choices:
            'Gaussian'

    prior_choices - list of current prior choices (see above)
    prior_scale - the overall scale of the prior variance
    prior_scale_orig - prior scale at the origin - generally set huge
                           to allow data to determine overall scale

    All of the above prior* variables are obsolescent.  Prefer the new
    _prior  - <AbstractPrior>

    The next 2 items might be obsolescent.  However, their presence permits us to
    set the parameter type before the image is loaded; _prior needs image info,
    specifically dimensions, for construction.
    param_func_type is replaced by _prior, specifically _prior.name(), 
    and param_func_choices should come from import priors
    param_func_type - string specifying the k-space BIFS paramter
                      function to use
                      current choices:
                      "Inverse Power Decay"
                      "Banded Inverse Power Decay"
                      "Linear Decay"
                      "Empirical"
    param_func_choices - list of current choices (see above)


    likelihood - string specifying likelihood distribution to use
                 current choices:
                 'Gaussian'
                 'Rician'

    likelihood_choices - list of current choices (see above)
    likelihood_scale - the assumed (const) noise level in k-space

    bessel_approx_lims - limits for bessel approximtion for rice
                         distribution - see paper referenced in code

    bessel_approx_array - array for bessel approximtion for rice
                         distribution - see paper referenced in code
    
    rice_denom_cutoff - cutoff for the demoninator of the closed form 
                        of the posterior with a Gaussian prior and
                        Rician likelihood derived from bessel approximation
                        see paper referenced in code

    basis - string specifying the basis to use - currently ony choice
            is "Fourier"
    basis_choices - list of current choices (see above)

    We continue to use bumps, but they mostly live in the prior.  We retain some info 
    here for compatibility with the GUI.

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


    Signals
    -------
    These are Qt signals, the reason the class must inherit from QObject.

    image_loaded - initial image has been loaded
    image_unloaded -  image has been unloaded

    """

    image_loaded = Signal()
    image_unloaded = Signal()
    
    def __init__(self,prior = "Gaussian",likelihood = "Gaussian",likelihood_scale = 0.05,prior_scale=0.0005,basis="Fourier"):
        """ 
       
        initializes class

        Inputs:
          prior - function type for prior
          likelihood - function type for likelihood
          likelihood_scale_orig - likelihood scale at k-space origin
          prior_scale - prior scale at k-space origin
          basis - basis type for transfrom space 

        Outputs:
          initializes class

        """

        super().__init__()

        self._invalidate_initial_image()
        self.view3Dslice = [0,0.5]

        self.prior = prior
        self.prior_choices = ["Gaussian"]
        self.prior_scale = prior_scale
        self.prior_scale_orig = 10.**7
        self._prior = None  # will hold <AbstractPrior> object
        self.param_func_choices = FP.param_func_choices()

        self.likelihood = likelihood
        self.likelihood_choices = ["Gaussian","Rician"]
        self.likelihood_scale = likelihood_scale
        self.rice_denom_cutoff = 0.0002
        
        # The following 3 parameters are used in conjuction
        # with a closed form for the posterior MAP estimate
        # with a Gaussian prior and Rician likelihood obtained
        # using sympy and based on an approximation to the first
        # order modified Bessel function discussed in:
        # A Simple and Efficient Approximation to the Modified Bessel
        # Functions and Its Applications to Rician Fading
        #     Ramy Salahat, Ehab Salahat, Ali Hakam and Tasneem Assaf
        # 2013 IEEE GCC Conference and exhibition, November 17-20, Doha, Qatar
        #
        self.bessel_approx_lims = np.array([0.0,11.5,20.0,37.5])
        self.bessel_approx_array  = np.array([[0.7536,0.4710,0.9807,1.144],
                                              [0.9739,-163.40,0.8672,0.995],
                                              [-0.715,0.9852,1.0795,0.5686],
                                              [0.2343,0.8554,1.0385,0.946]])
        self.basis_choices = ["Fourier"]
        self.basis = basis
        self.bas = None
        self.bumps = {}
        # Expand the following to if/else when more basis choices added
        # For now set default parameters here; make them editable via
        # pop widget
        if self.basis == "Fourier":
            from bifs.bases import fourier as fb
            self.bas = fb
        else:
            raise BifsBadInputs("Unknown basis: {}".format(self.basis))

        self.param_func_type = self.bas.param_func_type
        ##### Test 1 ##############
        ##### - These are the 'ideal' settings for a Rician
        ##### likelihood analysis
        # self.rice_denom_cutoff = 0.00025
        # self.likelihood = "Rician"
        # self.likelihood_scale = 0.0005
        # self.prior_scale = 0.00009
        ##### Test 1 ###############
        
    def _invalidate_initial_image(self):
        "Existing image, if any, and all that depends on it, is obsolete"
        self._init_image = None
        self.imdim = None
        self.image_file_loaded = False
        self.image_unloaded.emit()
        self.initial_image_file_name = ''
        self._prior = None  # depends on image dimensions
        self._invalidate_kspace()

    def _invalidate_kspace(self):
        """
        The transformation to k-space has or will change.
        Everything that depends on it is invalid
        """
        self._kdist = None
        self._k_image = None
        self._mod_image = None
        self._phase_image = None
        self._invalidate_final()

    def _invalidate_final(self):
        """
        The mapping from the k-space image to the final image has changed.
        Invalidate everything that depends on it.
        """
        self._final_image = None
        self._bifsk_image = None

    def save_results(self):
        """

        pickles current bifs object and saves to a time stamped file
        using jsonpickle; in addition saves processed final image and 
        final transform space image to files with the same time stamp 
        in case user just wants copies of final images without having 
        to reload bifs object.

        Inputs:

          current bifs object
         
        Outputs:
          saves time stamped files containing images and bifs parameters

        """
        # Date stamp for parameter output file
        date_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Output file names
        if self.image_file_loaded:
            # Assume here that input file is in standard 2 section,
            # period seperated form with file suffix as image type
            # First strip off any possible preceeding directory names
            in_file_name = self.initial_image_file_name
            in_file = in_file_name.split('/')[-1]
            file_prefix = in_file.split('.')[0]
            image_type = in_file.split('.')[1]
        else:
            # file_prefix = 'bifs_np_array_input'
            in_file_name = "Numpy Array"
            image_type = 'bmp'
            
        # Parameter file:
        out_p = 'bifs_params_'+date_stamp+'.bifspout'
        out_im = 'bifs_output_image_'+date_stamp+'.'+image_type
        out_k = 'bifs_output_kspace_'+date_stamp+'.'+image_type
        # Center final K-space image
        out_k_im = np.roll(np.roll(self.bifsk_image(),self.bifsk_image().shape[0]//2+1,0),self.bifsk_image().shape[1]//2,1)
        # Output images
        plt.imsave(out_im,self.final_image(),cmap = cm.Greys_r)
        plt.imsave(out_k,np.log(out_k_im),cmap = cm.Greys_r)
        # Output paramter file
        param_file = open(out_p, "w")
        param_file.write(jsp.encode(self))
        param_file.close()
        return

    def copy_params(self):
        """

        Return a new bifs object that has all the basic parameter values found in self.

        Does not copy the image or filename
        """
        newbifs = BIFS()
        newbifs.param_func_type = self.param_func_type
        newbifs.prior = self.prior
        newbifs.prior_scale = self.prior_scale
        newbifs._prior = copy.deepcopy(self._prior)
        newbifs.likelihood = self.likelihood
        newbifs.likelihood_scale = self.likelihood_scale
        newbifs.bumps = self.bumps
        newbifs.view3Dslice = self.view3Dslice
        return newbifs


    def load_image_file(self,fileName):
        """
        
        load an image file using name fileName; can use to
        examine image without invoking full bifs initialization.
        
        Inputs:
          fileName - name of file to load

        Outputs:
          loads file into bifs object

        RB makes read_imfile persistent in some cases so bulk scans can get the headers.

        """
        self._invalidate_initial_image()
        self.initial_image_file_name = fileName
        try:
            # For now the convention is that 1D data sets
            # will have filennames ending in '.txt' and
            # will be in numpy text file form, e.g. as created
            # with numpy.savetxt with the conventions that
            # header comments start with # and there is no
            # sperator between lines
            if self.initial_image_file_name.lower().endswith('.txt'):
                # numpy.loadtext automatacilly reads to numpy array
                read_image = np.loadtxt(self.initial_image_file_name)
            else:
                try:
                    import nibabel
                    # if nibabel is not installed, move on
                    # if nibabel can't read file, move on
                    # nibabel.streamlines.is_supported(fname) would seem to be a good test, but files
                    # that fail it can still be read, e.g., nii.gz files.
                    # So we use the Python idiom "Better to ask forgiveness than permission"
                    self.read_imfile = nibabel.load(self.initial_image_file_name)
                    read_image = self.read_imfile.get_fdata()
                except:
                    try:
                        self.read_imfile = imageio.volread(self.initial_image_file_name)
                        assert len(self.read_imfile) > 2
                        read_image = np.asarray(self.read_imfile)
                    except:
                        # we have a 2D, or maybe 1D, image
                        self.read_imfile = imageio.imread(self.initial_image_file_name)
                        read_image = np.asarray(self.read_imfile)
            self.load_image(read_image, invalidate=False)
        except Exception as exc:
            raise BifsBadInputs(f"BIFS Couldn't read image file: {fileName}") from exc
        return

    def load_image(self, init_image, invalidate=True):
        """

        intializes the bifs object so as to be ready for
        analysis steps.

        load_image_file calls this

        Inputs:

           init_image - array generated by loading image file using
                       load_image_file()
           invalidate - if True, clear caches.  Only very knowledgeable clients should use
                        this set to False

        """
        if invalidate:
            self._invalidate_initial_image()
        self._init_image = init_image
        self._init_image[np.isnan(init_image)] = 0.0
        self.imdim = len(init_image.shape)
        if not self.imdim in [1, 2, 3]:
            raise BifsBadInputs(f"Images with {self.imdim} dimensions are not supported.  Must be 1, 2, or 3 dimensions.")
        self.image_file_loaded = True
        self.image_loaded.emit()
        return

    def init_image(self):
        "Return initial image, if any"
        # For consistency with other accessors
        # if it's not there, we can't do anything
        return self._init_image

    def kdist(self):
        if self._kdist is None:
            myShape = self._init_image.shape
            if self.imdim == 1:
                self._kdist = self.bas.kdist1D(*myShape)
            elif self.imdim == 2:
                self._kdist = self.bas.kdist2D(*myShape)
            elif self.imdim == 3:
                self._kdist = self.bas.kdist3D(*myShape)
        return self._kdist

    def k_image(self):
        if self._k_image is None:
            if self.imdim == 1:
                self._k_image = self.bas.tx1(self._init_image) # Get k-space image
            elif self.imdim == 2:
                self._k_image = self.bas.tx2(self._init_image) # Get k-space image
            elif self.imdim == 3:
                self._k_image = self.bas.txn(self._init_image) # Get k-space image
            else:
                raise BifsBadInputs(f"1, 2, or 3 dimensional images supported. {self.imdim} dimensions are not supported." )
        return self._k_image

    def _final_setup(self):
        """Setup after image loaded and all other parameters are set.
        This used to be part of load_image, but was vulnerable to
        making calculations based on parameters that would later change.

        This should mostly be delegated to a suitable basis object.
        """
        
        if self.basis == "Fourier": # Add other basis functions as else...
            self._mod_image = abs(self.k_image()) # Get modulus image in k-space
            # sp.angle is deprecated
            self._phase_image = np.angle(self.k_image()) # Get phase image in k-space
            # self.data_std =  self.likelihood_scale*self.mod_image
            self.image_exists = True
        else:
            raise BifsBadInputs(f"{self.basis} basis unsupported.  Use Fourier.")

        # Set prior via orthogonal-space parameter function
        self.set_prior_func_type(self.param_func_type)
        # Set Rice parameter in case you use it
        # self.rice_arg = self.mod_image/self.likelihood_scale


        #### - The following doesn't seem to work, i.e. de-emphasizes -  ####
        #### - prior to too large an extent - need to investigate this - ####
        # Do normalization
        # # Since modulus and parameter functions are positive definite
        # don't need to square them (i.e. k-space integral) to get power
        # self.norm = (np.sum(self.mod_image))/(np.sum(self.prior_mean))
        # self.prior_mean = self.norm*self.prior_mean
        # self.prior_std = self.norm*self.prior_std
        # data std is regarded as constant, related to SNR
        # need to figure out best way to estimate and normalize
        ####                                                             ####
        ####                                                             ####
        
        return

    def mod_image(self):
        "Return modulus of k-space image"
        if self._mod_image is None:
            self._final_setup()
        return self._mod_image

    def phase_image(self):
        "return phase of k-space image"
        if self._phase_image is None:
            self._final_setup()
        return self._phase_image

    def final_image(self):
        "return final image in conventional space"
        if self._final_image is None:
            self.BIFS_MAP()
        return self._final_image

    def bifsk_image(self):
        "return final image in k-space"
        if self._bifsk_image is None:
            self.BIFS_MAP()
        return self._bifsk_image

    def add_bump(self,my_key,position,amplitude,width):
        """

        adds a bump filter to the self.bumps dictionalry

        Inputs:
           my_key - the name of an appropriate scipy.signal shape
           position -  fraction of kmax for location of bump filter
           amplitude - fraction of maximum of parameter function 
                       for amplitudeof of bump filter 
           width -     fraction of kmax for width of bump filter        

        Outputs:
          adds bump filter to prior

        """
        self._invalidate_final()
        return self.prior_object().add_bump(my_key, position, amplitude, width)


    def set_prior_func_type(self, pft : str):
        """ Set up prior object
        pft is the name of a type of prior function
        """
        if not self.image_file_loaded:
            self.param_func_type = pft
            self._prior = None
            # Nothing more can be done until image is loaded
            return
        if self._prior is not None and pft == self._prior.name():
            return
        self._invalidate_final()
        # test ##########
        # The following doesn't work and I don't know why
        # It seems that the prior function (in particulr the decay
        # function) should be normalized by the zero k-space value
        # of the image (i.e. the total "power") rather than an arbitrary
        # value like 500
        # self.bvec[1] = self.mod_image[0,0]
        # print("Zero k-space value:",self.mod_image[0,0])
        # self.bvec[1] = 50.0
        # test ##########
        if self.basis == "Fourier": # the usual re. elses for other tx spaces
            # Try setting bvec[1] = self.mod_image[0]
            # if self.imdim == 1:
            #    self.bvec[1] = self.mod_image[0]
            # elif self.imdim == 2:
            #    self.bvec[1] = self.mod_image[0,0]
            # elif self.imdim == 3:
            #    self.bvec[1] = self.mod_image[0,0,0]
            # else:
            #    pass
            if pft == "Inverse Power Decay":
                self._prior = FP.InversePowerDecayPrior(self.bas, self.kdist(), scale = self.prior_scale, scale_origin = self.prior_scale_orig)
            elif pft == "Banded Inverse Power Decay":
                self._prior = FP.BandedInversePowerDecayPrior(self.bas, self.kdist(), scale = self.prior_scale, scale_origin = self.prior_scale_orig)
            elif pft == "Linear Decay":
                self._prior = FP.LinearDecayPrior(self.bas, self.kdist(), scale = self.prior_scale, scale_origin = self.prior_scale_orig)
            elif pft == "Empirical":
                # This should already have been handled via set_empirical()
                assert self._prior.name() == "Empirical"
            else:
                raise BifsBadInputs("Please specify recognized transform space parameter function, one of:"+
                                   ", ".join(self.param_func_choices))
            self.param_func_type = pft
        else:
            raise BifBadInputs(f"{self.basis} basis unsupported.  Use Fourier.")

    def prior_object(self, invalidate=True):
        """ Return object representing the prior for possible editing.
        Edits may change the type-specific parameters of the object,
        but not the type (functional form) of the object.

        The ugly name is a result of prior already being used as a string.
        It should be the case that self.prior == self.prior_object().distribution().

        Also, the whole interface is ugly.

        Set invalidate=False only if you are not modifying the prior.
        """
        if invalidate:
            self._invalidate_final()
        if self._prior is None:
            self.set_prior_func_type(self.param_func_type)
        return self._prior

    def load_empirical(self, fname):
        """Load empirical prior from named file and set mode to Empirical
        """
        x = np.load(fname)
        return self.set_empirical(x)


    def set_empirical(self, x):
        """x is an object with the mean and sd of distn at each voxel
        It is presumed to be empirically derived, though you could make one up
        if you wanted to.

        Sets prior scale to 1, since the default value is very small.
        You can and probably should make it larger via the Gaussian gui specification.

        Note that because this requires self.bas and self.kdist the *image must be loaded first*.
        """
        self._invalidate_final()
        self._prior = EP.EmpiricalPrior(x, self.bas, self.kdist(), scale = 1.0, scale_origin = self.prior_scale_orig)
        self.param_func_type = "Empirical"

    def bifs_map_gauss_gauss(self, prior, mf, ds2):
        """
        returns MAP estimate for posterior function using 
        gaussian prior and likelihood and uses analytic 
        conjugate function

        Inputs:
           prior - <AbstractPrior>
           mf - k-space modulus (from data)
           ds2 - square of likelihood std

        Outputs:
           MAP estimate

        """
        # return((pm/ps2 + mf/ms2) / (1./ps2 + 1./ms2))
        # more efficient:
        return((prior.mean()*ds2 + mf*prior.var()) / (prior.var() + ds2))

    # Don't think the arguments to the prior and likelihood are
    # right yet, e.g. maybe need self.prior_mean_orig as argument
    # for scale factor of Gaussian prior - need to estimate the
    # the scale factor for the Rician from the signal to noise
    # in the image... KY
    
    def bifs_map_gauss_rice(self, prior, mf, ds):
        """
        returns MAP estimate for posterior function using 
        gaussian prior and rician likelihood and uses uses analytic
        function derived using sympy and the modified Bessel
        function approximation from the paper cited above
        
        Inputs:
           prior - <AbstractPrior>
           mf - k-space modulus (from data)
           ds - data std
        Outputs:
           MAP estimate
        """
        # Kludge - slows things down but we use the Gaussian conjugate
        # prior calculation to estimate where the MAP value will be and
        # ergo estimate which of the exponential coefficient values to use
        # for the modified Bessel function approximation
        #
        conj = self.bifs_map_gauss_gauss(prior, self.mod_image, self.ksd2)
        d = (2*ds**2 - 2*prior.var())
        dabs = np.abs(d)
        # Estimate which Bessel approximation coefficients
        # to use based on the Gaussian conjugate MAP value

        sn = np.zeros(d.shape)
        sn = where(np.abs(d) > 0,np.sign(d),-1.0)
        denom = sn*np.maximum(np.abs(d),self.rice_denom_cutoff)
        b = mf/ds
        result = 0.0
        for i in range(self.bsa.shape[-1]):
            if self.imdim == 1:
                ba = self.bsa[:,i]
            elif self.imdim == 2:
                ba = self.bsa[:,:,i]
            elif self.imdim == 3:
                ba = self.bsa[:,:,:,i]
            else:
                pass
            num = (-(b*ba*ds*prior.var() - mf*ds**2 + 2*mf*prior.var() - ds**2*prior.mean() + 
                     ds*np.sqrt(b**2*ba**2*prior.var()**2 + 2*b*ba*mf*ds*prior.var() - 2*b*ba*ds*prior.mean()*prior.var() +
                               mf**2*ds**2 - 2*mf*ds**2*prior.mean() + ds**2*prior.mean()**2 - 4*ds**2*prior.var() + 4*prior.var()**2)))
            ### Note - the closer the scales get to each other
            # (ergo the pathalogical blow up), the MAP estimate
            # should actually get closer to the average of the
            # the prior mean and likelihood mean - that's the
            # logic for:
            # denom = np.where(dabs < self.rice_denom_cutoff,(2*num)/(mf+pm),dabs)
            ### Doesn't seem to work so back to above denom setting with
            ### cutoff
                
            result += (num/denom)/len(ba.shape)
        # Need to include the sign part here in case the setting
        # for the denominator screwed up the sign
        return np.sign(result)*result
        
    def BIFS_MAP(self):
        """

        performs MAP optimization individually at each k-space 
        point using the MAP estimation functions above,
        recombines the results, performs inverse transform and returns final image.

        This seemed like a good place to use the multiprocessing package, but initial
        testing found that to be slower, and so we removed the code.

        Inputs:

        Outputs:
          Sets final_image based on performing k-space MAP estimation 

        """
        # Break up image(s) into linear array(s) for sending off
        # to multiprocessing - this is stupid and unecessarily
        # time consuming but I still need to figure out how to send
        # chunks of multivariate arrays to a multiprocessing pool
        if not self.image_file_loaded:
            raise BifsBadInputs("Error: Need to load an image before running MAP")
        self._final_setup()

        # Square of likelihood
        self.ksd2 = self.likelihood_scale**2
        # self.data_std2 = self.data_std**2
        # Rician parameter
        # self.rice_arg = self.mod_image/self.likelihood_scale
        if self.prior == "Gaussian" and self.likelihood == "Gaussian":
            self._bifsk_image = self.bifs_map_gauss_gauss(self._prior, self.mod_image(), self.ksd2)
        elif self.prior == "Gaussian" and self.likelihood == "Rician":
            conj = self.bifs_map_gauss_gauss(self._prior, self.mod_image(), self.ksd2)
            besind = np.zeros(self._init_image.shape, dtype=int)
            besind[np.where(conj > self.bessel_approx_lims[1])] = 1
            besind[np.where(conj > self.bessel_approx_lims[2])] = 2
            besind[np.where(conj > self.bessel_approx_lims[3])] = 3
            self.bsa = self.bessel_approx_array[besind,:]
            self._bifsk_image = self.bifs_map_gauss_rice(self._prior, self.mod_image(), self.likelihood_scale)
        else:
            raise BifsBadInputs(f"Unable to calculate with {self.prior} prior and {self.likelihood} likelihood.")
        # Send back to image space
        if self.basis == "Fourier": # usual add else for other tx 
            if self.imdim == 1:
                self._final_image = np.real(self.bas.itx1(self._bifsk_image*np.exp(1j*self.phase_image())))
            elif self.imdim == 2:
                self._final_image = np.real(self.bas.itx2(self._bifsk_image*np.exp(1j*self.phase_image())))
            elif self.imdim == 3:
                self._final_image = np.real(self.bas.itxn(self._bifsk_image*np.exp(1j*self.phase_image())))
        else:
            raise BifsBadInputs(f"{self.basis} basis unsupported.  Use Fourier.")
        return
