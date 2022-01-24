import math
import numpy as np
from ..resources.logger import LoggerOrPrint
from ..misc import fourier_filters
from ..misc.padding import pad_interpolate, recut


class GeoPars:
    """
    A class to describe the geometry of a phase contrast radiography with
    a source obtained by a focussing system, possibly astigmatic, which is
    at distance z1_vh from the sample. The detector is at z2 from the sample
    """

    def __init__(
        self,
        z1_vh=None,
        z2=None,
        pix_size_det=None,
        wavelength=None,
        magnification=True,
        length_scale=10.0e-6,
        logger=None,
    ):
        """
        Parameters
        ----------
        z1_vh : None, a float, or a sequence of two floats
           the source sample distance (meters), if None the parallel beam is assumed.
           If two floats are given then they are taken as the distance of the vertically focused source (horizontal line)
           and the horizontaly focused source (vertical line) for KB mirrors.
        z2 : float
           the sample detector distance (meters).
        pix_size_det: float
           pixel size (meters)
        wavelength: float
           beam wave length (meters).
        magnification: boolean defaults to True
           if false no magnification is considered
        length_scale: float
            rescaling length scale, meant to avoid having too big or too small numbers.
            defaults to 10.0e-6
        logger: Logger, optional
            A logging object
        """
        self.logger = LoggerOrPrint(logger)
        if z1_vh is None:
            self.z1_vh = None
        else:
            if hasattr(type(z1_vh), "__iter__"):
                self.z1_vh = np.array(z1_vh)
            else:
                self.z1_vh = np.array([z1_vh, z1_vh])
        self.z2 = z2
        self.magnification = magnification
        self.pix_size_det = pix_size_det

        if self.magnification and self.z1_vh is not None:
            self.M_vh = (self.z1_vh + self.z2) / self.z1_vh
        else:
            self.M_vh = np.array([1, 1])

        self.logger.debug("Magnification : h ({}) ;  v ({}) ".format(self.M_vh[1], self.M_vh[0]))

        self.length_scale = length_scale
        self.wavelength = wavelength

        self.maxM = self.M_vh.max()

        self.pix_size_rec = self.pix_size_det / self.maxM  # we bring everything to highest magnification

        which_unit = np.sum(np.array([(self.pix_size_rec > small) for small in [1.0e-6, 1.0e-7]]).astype(np.int32))
        self.pixelsize_string = [
            "{:.1f} nm".format(self.pix_size_rec * 1e9),
            "{:.3f} um".format(self.pix_size_rec * 1e6),
            "{:.1f} um".format(self.pix_size_rec * 1e6),
        ][which_unit]

        if self.magnification:
            self.logger.debug(
                "All images are resampled to smallest pixelsize: {}".format(self.pixelsize_string),
            )
        else:
            self.logger.debug("Pixelsize images:  {}".format(self.pixelsize_string))


class CTFPhaseRetrieval:
    def __init__(self, geo_pars, delta_beta, lim1=1.0e-5, lim2=0.2, use_rfft=False, logger=None):
        """
        This class implements the CTF formula (see equation 8 in Boliang Yu et al
        Optic Express Vol 26, No 9, 2018) in its regularised form which avoids the zeros
        of unregularised_filter_denominator
        (unreg_filter_denom is the so here named denominator/delta_beta of equation 8)

        Parameters
        ----------
        geo_pars: GeoPars
            the geometry description
        delta_beta : float
            the delta/beta ratio
        lim1: float >0
            the regulariser strenght at low  frequencies
        lim2: float >0
            the regulariser strenght at high frequencies
        use_rfft: bool, optional
            Whether to use real-to-complex (R2C) FFT instead of usual complex-to-complex (C2C).
        logger: optional
            a logger object
        """
        self.logger = LoggerOrPrint(logger)
        self.setup(geo_pars, delta_beta, lim1=lim1, lim2=lim2, use_rfft=use_rfft)

    def setup(self, geo_pars, delta_beta, lim1=None, lim2=None, use_rfft=False):
        """
        Set up the current geometrical parameters.

        Parameters
        -----------
        geo_pars: GeoPars
            The eometry of the experiment
        delta_beta : float,
            The delta/beta ratio in single-distance phase retrieval
        lim1: float >0
            The regulariser strength at low frequencies
        lim2: float >0
            The regulariser strength at high frequencies
        """
        if not isinstance(geo_pars, GeoPars):
            raise ValueError("Expected GeoPars instance for 'geo_pars' parameter")

        self.lim = None
        # these parameters will be stored for pipelining: if the shape changes in a call
        # to retrieve_phase the filter will be recalculated for that shape
        self.lim1 = lim1
        self.lim2 = lim2
        self.delta_beta = delta_beta
        self.geo_pars = geo_pars
        self.filter_is_ready = False
        self.filter_shape = None
        self.use_rfft = use_rfft
        self._fft_func = np.fft.rfft2 if use_rfft else np.fft.fft2
        self._ifft_func = np.fft.irfft2 if use_rfft else np.fft.ifft2


    def require_filter_for_shape(self, padded_img_shape):
        if self.filter_is_ready and self.filter_shape == padded_img_shape:
            return
        else:
            self.filter_is_ready = False
            self.filter_shape = None

        ## the parameter "length_scale" was mentioned, in the octave code,
        ## as a rescaling length scale, which is meant to avoid
        ## having too big or too small numbers.
        ## From the mathematical point of view, it is infact completely trasparent:
        ## its action is on fsamplex, fsampley and  betash, betasv.
        ## But these latters ( beta's)  are multiplied by  the formers (fsample's) so that
        ## "length_scale" mathematically disappears, however in case of simple precision float
        ## the exponent of a float number ranges from -38 to 38, and one could approach it
        ## as an example by taking the square of a very small number ( 1.0e-19), and losing significant bits
        ## in he mantissa or getting zero, or the square of a big number, thus generting inf
        ## Althought the values involved in our x-ray regimes seems safe, with respect to these problems,
        ## this length_scale parameters does not hurt.
        fsample_vh = np.array(
            [self.geo_pars.length_scale / self.geo_pars.pix_size_rec, self.geo_pars.length_scale / self.geo_pars.pix_size_rec]
        )

        if not self.use_rfft:
            ff_index_vh = list(map(np.fft.fftfreq, padded_img_shape))
        else:
            ff_index_vh = [np.fft.fftfreq(padded_img_shape[0]), np.fft.rfftfreq(padded_img_shape[1])]

        # if padded_img_shape[1]%2 == 0 : # change to holotomo_slave indexing (by a transparent 2pi shift)
        #     ff_index_x[ ff_index_x  == -0.5    ] =  +0.5
        # if padded_img_shape[0]%2 == 0 : # change to holotomo_slave indexing (by a transparent 2pi shift)
        #     ff_index_y[ ff_index_y  == -0.5    ] =  +0.5

        frequencies_vh = np.array(
            np.meshgrid(ff_index_vh[0] * fsample_vh[0], ff_index_vh[1] * fsample_vh[1], indexing="ij")
        )

        frequencies_squared_vh = frequencies_vh * frequencies_vh

        ## ---------------  fresnelnumbers and forward propagators -------------------
        ## In the limit of parallel beam, z1_h and z1_v would be infinite
        ## so that the here below distances becomes z2
        ## which is sample-detector distance.
        ##

        if self.geo_pars.z1_vh is not None:
            distances_vh = (self.geo_pars.z1_vh * self.geo_pars.z2) / (self.geo_pars.z1_vh + self.geo_pars.z2)
        else:
            distances_vh = np.array([self.geo_pars.z2, self.geo_pars.z2])

        ## Citing David Paganin (2002) :
        ## The intensity I_{R_1}(r⊥,z) at a distance z  of a weakly refracting object illuminated by a
        ## point source at distance R1  behind the said object, is related to the intensity
        ## I∞(r⊥,z), which would result from normally
        ## incident collimated illumination of the same object, by (Pogany et al., 1997):
        ##   I_{R_1}(r⊥,z) = 1/{M^2} I∞(r⊥/M , z/M)
        ## where M is the magnification.
        ## This explains the effective distance formula expressed by
        ## distancesh, distancesv  above.
        ## ------------------------------------------------------------------------------

        lambda_dist_vh = self.geo_pars.wavelength * distances_vh / (self.geo_pars.length_scale ** 2)

        ## ---------------------------------------------------------------------------------------
        ## -> cut_v at first maximum of ctf largest distance
        ##
        ## In the paraxial expansion of the Fresnel propagator, the phase is equal to
        ##                   1/2 K_{parallel}^2 wavelength * Distance /2 / pi
        ##
        ## When this is equal to a multiple of 2 pi, the effect of propagation disappears
        ## and we have a singularity in equation 8.
        ##
        ## The sampling in the reciprocal space is done with  a step length of 2*pi*fsamplex,y
        ##   (note: fsamples are the plain inverse of pixel size)
        ## The first singularity occurs  at a frequence number
        ##                 K_{parallel}/2/pi/ fsamplex
        ##
        ##  for K_{parallel}^2 = 2 * (2pi)^2 /( wavelength * distance  )
        ##
        ##  which would correspond to
        ##            K_{parallel}/2/pi/ fsamplex  =  sqrt( 2/wavelength*distance) / fsample
        ##
        ## Question:( why the factor 2 appear at the denominator in the square root below?)
        ## Answer : the below defined cut corresponds to the first maximum of the denominator,
        ## before arriving to the first zero. In this way the regularisation
        ## is already at ( almost) full strenght on the first pole.
        self.cut_v = math.sqrt(1.0 / 2 / lambda_dist_vh[0]) / fsample_vh[0]
        self.cut_v = min(self.cut_v, 0.5)

        self.logger.debug("Normalized cut-off = {:5.3f}".format(self.cut_v))

        self.r = fourier_filters.get_lowpass_filter(
            padded_img_shape,
            cutoff_par=(
                0.5 / (self.cut_v + 1.0 / padded_img_shape[0]),
                0.01 * padded_img_shape[0] / (1 + self.cut_v * padded_img_shape[0]),
            ),
            use_rfft=self.use_rfft
        )
        self.r /= self.r[0, 0]

        self.lim = self.lim1 * self.r + self.lim2 * (1 - self.r)

        # more methods exist in the original code, and they are initialized starting from here
        # (ht_app1, ht_app2... ht_app7)

        fresnel_phase = (
            np.pi * lambda_dist_vh[1] * frequencies_squared_vh[1] + np.pi * lambda_dist_vh[0] * frequencies_squared_vh[0]
        )

        if self.delta_beta:
            self.logger.debug(
                "Taking into account absorption assuming homogeneous object.\n"
                "Set delta_beta = 0 if this is not the purpose."
            )
            unreg_filter_denom = np.sin(fresnel_phase) + (1.0 / self.delta_beta) * np.cos(fresnel_phase)
        else:
            unreg_filter_denom = np.sin(fresnel_phase)

        self.unreg_filter_denom = unreg_filter_denom

        self.filter_is_ready = True
        self.filter_shape = padded_img_shape

    def _apply_filter(self, img):
        self.require_filter_for_shape(img.shape)

        img_f = self._fft_func(img)
        firec0 = self.unreg_filter_denom * img_f
        unreg_filter_denom_0_mean = self.unreg_filter_denom[0, 0]
        nf, mf = img.shape

        # here it is assumed that the average of img is 1 and the DC component is removed
        firec0[0, 0] -= nf * mf * unreg_filter_denom_0_mean

        ## formula 8, with regularisation to stay at a safe distance from the poles
        ph = firec0 / (2 * self.unreg_filter_denom * self.unreg_filter_denom + self.lim)
        ph = self._ifft_func(ph).real
        return ph


    def retrieve_phase(self, img, padded_shape="auto", padding_mode="reflect", translation_vh=None, normalize_by_mean=False):
        """
        Apply the CTF filter to retrieve the phase.

        Parameters
        ----------
        img: np.ndarray
            Projection image. It must have been already flat-fielded.
        padded_shape: str or tuple, optional
            Padded image shape, in the form (num_rows, num_columns) i.e (vertical, horizontal).
            By default, it is twice the image shape.
        padding_mode: str
            Padding mode. It must be valid for the numpy.pad function
        translation_vh: array, optional
            Shift in the form (y, x). It is used to perform a translation of the image before applying the CTF filter.
        normalize_by_mean: bool
            Whether to divide the (padded) image with its mean before applying the CTF filter.

        Returns
        --------
        ph: numpy.ndarray
            Phase image
        """
        if padded_shape is None or padded_shape is False:
            padded_shape = img.shape # no padding
        elif isinstance(padded_shape, (tuple, list, np.ndarray)):
            pass
        elif padded_shape == "auto":
            padded_shape = (2 * img.shape[0], 2 * img.shape[1])

        padded_img = pad_interpolate(
            img, padded_shape, translation_vh=translation_vh, padding_mode=padding_mode
        )
        if normalize_by_mean:
            padded_img /= padded_img.mean()
        phase_img = self._apply_filter(padded_img)
        res = recut(phase_img, img.shape)
        return res


CtfFilter = CTFPhaseRetrieval