"""NGHXRG - Teledyne HxRG Noise Generator.

Modification History:

8-15 April 2015,  B.J. Rauscher,  NASA/GSFC
- Implement Pierre Ferruit's (ESA/ESTEC)recommendation to use
  numpy.fft.rfft and numpy.fft.irfft for faster execution. This saves
  about 30% in execution time.
- Clean up setting default values per several suggestions from
  Chaz Shapiro (NASA/JPL).
- Change from setting the shell variable H2RG_PCA0 to point to the PCA-zero
  file to having a shell variable point to the NG home directory. This is per
  a suggestion from Chaz Shapiro (NASA/JPL) that would allow seamlessly adding
  more PCA-zero templates.
- Implement a request form Chaz Shapiro (NASA/JPL) for status
  reporting. This was done by adding the "verbose" arguement.
- Implement a request from Pierre Ferruit (ESA/ESTEC) to generate
  3-dimensional data cubes.
- Implement a request from Pierre Ferruit to treat :term:`ACN` as different 1/f
  noise in even/odd columns. Previously :term:`ACN` was treated purely as a feature
  in Fourier space.
- Version 2(Beta)

16 April 2015,  B.J. Rauscher
- Fixed a bug in the pinkening filter definitions. Abs() was used where
  sqrt() was intended. The bug caused power spectra to have the wrong shape at
  low frequency.
- Version 2.1(Beta)

17 April 2015,  B.J. Rauscher
- Implement a request from Chaz Shapiro for HXRGNoise() to exit gracefully if
  the pca0_file is not found.
- Version 2.2 (Beta)

8 July 2015,  B.J. Rauscher
- Address PASP referee comments
    * Fast scan direction is now reversible. To reverse the slow scan
      direction use the numpy flipud() function.
    * Modifications to support subarrays. Specifically,
        > Setting reference_pixel_border_width=0 (integer zero);
            + (1) eliminates the reference pixel border and
            + (2) turns off adding in a bias pattern
                  when simulating data cubes. (Turned on in v2.5)
- Version 2.4

12 Oct 2015,  J.M. Leisenring,  UA/Steward
- Make compatible with Python 2.x
    * from __future__ import division
- Included options for subarray modes (FULL,  WINDOW,  and STRIPE)
    * Keywords wind_x0 and wind_y0 define a subarray position (lower left corner)
    * Selects correct pca0 region for subarray underlay
    * Adds reference pixel if they exist within subarray window
- Tie negative values to 0 and anything >=2^16 to 2^16-1
- Version 2.5

20 Oct 2015,  J.M. Leisenring,  UA/Steward
- Padded nstep to the next power of 2 in order to improve FFT runtime
    * nstep2 = int(2**np.ceil(np.log2(nstep)))
    * Speeds up FFT calculations by ~5x
- Don't generate noise elements if their magnitudes are equal to 0.
- make_noise() now returns copy of final HDU result for easy retrieval
- Version 2.6

29 Jan 2018,  David Lucsanyi, ESA/ESTEC
- Code has been made PEP8 compatible
- Fixed NGHXRG_HOME file path
- Fixed make_noise() variables
- Bug fixed in :term:`ACN` mask, now code works with any naxis1, naxis2 and n_out values not just default arguments
- Commented out unused code for :term:`ACN` arrays
- make_noise() function separated into different noise generator functions,
which returns result numpy array to be able to add to Pyxel detector signal
- removed STRIPE mode (did not work), use WINDOW instead -> BUG: code doesn't work with different x and y array sizes
- Integrated into Pyxel detector simulation framework via a wrapper function
- Version 2.7

20 Feb 2019,  David Lucsanyi, ESA/ESTEC
- use logging
- ZeroDivision error fixed
- Version 2.8
"""
import logging
import typing as t

import numpy as np
from astropy.io import fits
from astropy.stats.funcs import median_absolute_deviation as mad
from scipy.ndimage.interpolation import zoom
from typing_extensions import Literal


def white_noise(nstep: int) -> np.ndarray:
    """Generate white noise for an HxRG including all time steps (actual pixel and overheads).

    Parameters
    ----------
        nstep - Length of vector returned

    """
    distribution = np.random.standard_normal(nstep)  # type: np.ndarray
    return distribution


# TODO: Compare with https://github.com/astronomyk/SimCADO/blob/master/simcado/nghxrg.py
#       Later, we should use class 'simcado.nghxrg.HXRGNoise' instead of this class.
class HXRGNoise:
    """HXRGNoise is a class for making realistic Teledyne HxRG system noise.

    The noise model includes correlated,  uncorrelated,
    stationary,  and non-stationary components. The default parameters
    make noise that resembles Channel 1 of JWST NIRSpec. NIRSpec uses
    H2RG detectors. They are read out using four video outputs at
    1.e+5 pix/s/output.
    """

    # These class variables are common to all HxRG detectors
    NGHXRG_VERSION = 2.8  # Sofware version

    def __init__(
        self,
        det_size_x: int,
        det_size_y: int,
        time_step: int,
        n_out: int,
        nroh: int,
        nfoh: int,
        reverse_scan_direction: bool,
        reference_pixel_border_width: int,
        wind_mode: Literal["FULL", "WINDOW"],
        wind_x_size: int,
        wind_y_size: int,
        wind_x0: int,
        wind_y0: int,
        verbose: bool,
        pca0: np.ndarray,
    ):
        """Simulate Teledyne HxRG+SIDECAR ASIC system noise.

        Parameters
        ----------
            naxis1      - X-dimension of the FITS cube
            naxis2      - Y-dimension of the FITS cube
            time_step   - Z-dimension of the FITS cube, number of frame in series over time
                          (number of up-the-ramp samples)
            n_out       - Number of detector outputs
            nfoh        - New frame overhead in rows. This allows for a short
                          wait at the end of a frame before starting the next
                          one.
            nroh        - New row overhead in pixel. This allows for a short
                          wait at the end of a row before starting the next one.
            verbose     - Enable this to provide status reporting
            wind_mode   - 'FULL' or 'WINDOW' (JML)
            wind_x0/wind_y0       - Pixel positions of subarray mode (JML)
            det_size_x    - Pixel dimension of full detector (square),  used only
                          for WINDOW mode (JML)
            reference_pixel_border_width - Width of reference pixel border
                                           around image area
            reverse_scan_direction - Enable this to reverse the fast scanner
                                     readout directions. This
                                     capability was added to support
                                     Teledyne's programmable fast scan
                                     readout directions. The default
                                     setting =False corresponds to
                                     what HxRG detectors default to
                                     upon power up.
        """
        # ======================================================================
        #
        # DEFAULT CLOCKING PARAMETERS
        #
        # The following parameters define the default HxRG clocking pattern. The
        # parameters that define the default noise model are defined in the
        # make_noise() method.
        #
        # ======================================================================
        self._log = logging.getLogger("nghxrg")

        if wind_mode == "WINDOW":
            n_out = 1
            self.naxis1 = wind_x_size
            self.naxis2 = wind_y_size
        elif wind_mode == "FULL":
            wind_x0 = 0
            wind_y0 = 0
            self.naxis1 = det_size_x
            self.naxis2 = det_size_y
        # elif wind_mode == 'STRIPE':
        #     wind_x0 = 0
        else:
            raise ValueError("Not a valid window readout mode!")
            # _log.warning('%s not a valid window readout mode! Returning...' % inst_params['wind_mode'])  # ERROR WTF
            # os.sys.exit()

        self.naxis3 = 1  # always use only one frame (2d array)
        self.time_step = time_step  # number of frame over time
        self.n_out = n_out
        # self.dt = dt
        self.nroh = nroh
        self.nfoh = nfoh
        self.reference_pixel_border_width = reference_pixel_border_width
        # self.pca0_file = pca0_file

        # Default clocking pattern is JWST NIRSpec
        # if naxis1 is None:
        #     self.naxis1 = 2048
        # if naxis2 is None:
        #     self.naxis2 = 2048
        # if naxis3 is None:
        #     self.naxis3 = 1
        # if n_out is None:
        #     self.n_out = 4
        # if dt is None:
        #     self.dt = 1.e-5
        # if nroh is None:
        #     self.nroh = 12
        # if nfoh is None:
        #     self.nfoh = 1
        # if reference_pixel_border_width is None:
        #     self.reference_pixel_border_width = 4

        # Check that det_size_x is greater than self.naxis1 and self.naxis2 in WINDOW mode (JML)
        if wind_mode == "WINDOW":
            if self.naxis1 > det_size_x:
                raise ValueError()
                # _log.warning('NAXIS1 %s greater than det_size_x %s! Returning...' % (self.naxis1, det_size_x))
                # os.sys.exit()
            if self.naxis2 > det_size_y:
                raise ValueError()
                # _log.warning('NAXIS2 %s greater than det_size_y %s! Returning...' % (self.naxis1, det_size_y))
                # os.sys.exit()

        # ======================================================================

        # Configure Subarray (JML)
        self.wind_mode = wind_mode  # type: Literal["FULL", "WINDOW"]
        self.det_size_x = det_size_x
        self.det_size_y = det_size_y
        self.wind_x0 = wind_x0
        self.wind_y0 = wind_y0

        # Select region of pca0 associated with window position
        if self.wind_mode == "WINDOW":
            x1 = self.wind_x0
            y1 = self.wind_y0
        # elif self.wind_mode == 'STRIPE':
        #     x1 = 0
        #     y1 = self.wind_y0
        else:
            x1 = 0
            y1 = 0

        # print(y1, self.naxis2) This appears to be a stub
        x2 = x1 + self.naxis1
        y2 = y1 + self.naxis2

        # How many reference pixel on each border?
        w = self.reference_pixel_border_width  # Easier to work with
        lower = w - y1
        upper = w - (self.det_size_y - y2)
        left = w - x1
        right = w - (self.det_size_x - x2)
        ref_all = np.array([lower, upper, left, right])
        ref_all[ref_all < 0] = 0
        self.ref_all = ref_all

        # Configure status reporting
        self.verbose = verbose

        # Configure readout direction
        self.reverse_scan_direction = reverse_scan_direction

        # Compute the number of pixel in the fast-scan direction per output
        self.xsize = self.naxis1 // self.n_out

        # Compute the number of time steps per integration,  per output
        self.nstep = (
            (self.xsize + self.nroh) * (self.naxis2 + self.nfoh) * self.time_step
        )
        # Pad nsteps to a power of 2,  which is much faster (JML)
        self.nstep2 = int(2 ** np.ceil(np.log2(self.nstep)))

        # For adding in ACN, it is handy to have masks of the even
        # and odd pixel on one output neglecting any gaps
        # UNUSED CODE COMMENTED OUT
        # self.m_even = np.zeros((self.naxis3, self.naxis2, self.xsize))
        # self.m_odd = np.zeros_like(self.m_even)
        # for x in np.arange(0, self.xsize, 2):
        #     self.m_even[:, :self.naxis2, x] = 1
        #     self.m_odd[:, :self.naxis2, x+1] = 1
        # self.m_even = np.reshape(self.m_even,  np.size(self.m_even))
        # self.m_odd = np.reshape(self.m_odd,  np.size(self.m_odd))
        # UNUSED CODE COMMENTED OUT

        # Also for adding in ACN,  we need a mask that point to just
        # the real pixel in ordered vectors of just the even or odd pixel - BUG FIXED HERE (D.L.)
        self.m_short = np.zeros(
            (self.naxis3, (self.naxis2 + self.nfoh) // 2, self.xsize + self.nroh)
        )
        self.m_short[:, : self.naxis2 // 2, : self.xsize] = 1
        # self.m_short = np.reshape(self.m_short,  np.size(self.m_short))
        self.m_short = self.m_short.flatten()

        # Define frequency arrays
        self.f1 = np.fft.rfftfreq(
            n=self.nstep2, d=1.0
        )  # Frequencies for nstep elements
        self.f2 = np.fft.rfftfreq(n=2 * self.nstep2, d=1.0)  # ... for 2*nstep elements

        # Define pinkening filters. F1 and p_filter1 are used to
        # generate ACN. F2 and p_filter2 are used to generate 1/f noise.
        self.alpha = -1  # Hard code for 1/f noise until proven otherwise
        self.p_filter1 = np.sqrt(self.f1[1:] ** self.alpha)
        self.p_filter2 = np.sqrt(self.f2[1:] ** self.alpha)
        self.p_filter1 = np.insert(self.p_filter1, 0, 0.0)
        self.p_filter2 = np.insert(self.p_filter2, 0, 0.0)

        # if pca0_file is not None:
        #     # Initialize PCA-zero file and make sure that it exists and is a file
        #     # self.pca0_file = os.getenv('NGHXRG_HOME')+'/nirspec_pca0.fits' if \
        #     # if pca0_file is None:
        #     #     self.pca0_file = NGHXRG_HOME + '/nirspec_pca0.fits'
        #
        #     if pca0_file.exists() is False:
        #         self._log.error(
        #             "There was an error finding pca0_file! Check to be"
        #             "sure that the NGHXRG_HOME shell environment"
        #             "variable is set correctly and that the"
        #             "$NGHXRG_HOME/ directory contains the desired PCA0"
        #             "file. The default is nirspec_pca0.fits."
        #         )
        #         raise ValueError()
        #         # os.sys.exit()

        # Initialize pca0. This includes scaling to the correct size,
        # zero offsetting,  and renormalization. We use robust statistics
        # because pca0 is real data
        # hdu = fits.open(pca0_file)
        # nx_pca0 = hdu[0].header["naxis1"]
        # ny_pca0 = hdu[0].header["naxis2"]

        zoom_factor = 0
        # Do this slightly differently,  taking into account the
        # different types of readout modes (JML)
        # if (nx_pca0 != self.naxis1 or naxis2 != self.naxis2):
        #    zoom_factor = self.naxis1 / nx_pca0
        #    self.pca0 = zoom(hdu[0].data,  zoom_factor,  order=1,  mode='wrap')
        # else:
        #    self.pca0 = hdu[0].data
        # self.pca0 -= np.median(self.pca0) # Zero offset
        # self.pca0 /= (1.4826*mad(self.pca0)) # Renormalize

        data = pca0
        nx_pca0, ny_pca0 = pca0.shape

        # Make sure the real PCA image is correctly scaled to size of fake data (JML)
        # Depends if we're FULL, STRIPE or WINDOW
        if wind_mode == "FULL":
            scale1 = self.naxis1 / nx_pca0
            scale2 = self.naxis2 / ny_pca0
            zoom_factor = np.max([scale1, scale2])
        # if wind_mode == 'STRIPE':
        #     zoom_factor = self.naxis1 / nx_pca0
        if wind_mode == "WINDOW":
            # Scale based on det_size_x
            scale1 = self.det_size_x / nx_pca0
            scale2 = self.det_size_y / ny_pca0
            zoom_factor = np.max([scale1, scale2])

        # Resize PCA0 data
        if zoom_factor != 1:
            data = zoom(data, zoom_factor, order=1, mode="wrap")

        data -= np.median(data)  # Zero offset
        data /= 1.4826 * mad(data)  # Renormalize

        # Make sure x2 and y2 are valid
        if x2 > data.shape[0] or y2 > data.shape[1]:
            raise ValueError()
            # _log.warning('Specified window size does not fit within detector array!')
            # _log.warning('X indices: [%s, %s]; Y indices: [%s, %s]; XY Size: [%s,  %s]' %
            #              (x1, x2, y1, y2, data.shape[0], data.shape[1]))
            # os.sys.exit()
        self.pca0 = data[y1:y2, x1:x2]

    def pink_noise(self, mode: Literal["pink", "acn"]) -> np.ndarray:
        """Generate a vector of non-periodic pink noise.

        Parameters
        ----------
        mode : 'pink' or 'acn'
            Select mode for pink noise.

        Returns
        -------
        ndarray
        """
        # Configure depending on mode setting
        if mode == "pink":
            nstep = 2 * self.nstep
            nstep2 = 2 * self.nstep2  # JML
            # f = self.f2
            p_filter = self.p_filter2
        else:
            nstep = self.nstep
            nstep2 = self.nstep2  # JML
            # f = self.f1
            p_filter = self.p_filter1

        # Generate seed noise
        mynoise = white_noise(nstep2)

        # Save the mean and standard deviation of the first
        # half. These are restored later. We do not subtract the mean
        # here. This happens when we multiply the FFT by the pinkening
        # filter which has no power at f=0.
        the_mean = np.mean(mynoise[: nstep2 // 2])
        the_std = np.std(mynoise[: nstep2 // 2])

        # Apply the pinkening filter.
        thefft = np.fft.rfft(mynoise)
        thefft = np.multiply(thefft, p_filter)
        result = np.fft.irfft(thefft)  # type: np.ndarray
        result = result[: nstep // 2]  # Keep 1st half of nstep

        # Restore the mean and standard deviation
        result *= the_std / np.std(result)
        result = result - np.mean(result) + the_mean

        # if mode == 'acn':

        # Done
        return result

    # def make_noise(self, rd_noise=5.2, c_pink=3, u_pink=1, acn=0.5, pca0_amp=0.2,
    #                reference_pixel_noise_ratio=0.8, ktc_noise=29., bias_offset=5000., bias_amp=500.):
    #     """
    #     Generate a FITS cube containing only noise.
    #
    #     Parameters:
    #         rd_noise - Standard deviation of read noise in electrons
    #         c_pink   - Standard deviation of correlated pink noise in electrons
    #         u_pink   - Standard deviation of uncorrelated pink noise in
    #                    electrons
    #         acn      - Standard deviation of alternating column noise in
    #                    electrons
    #         pca0_amp - Standard deviation of pca0 in electrons
    #         reference_pixel_noise_ratio - Ratio of the standard deviation of
    #                                       the reference pixel to the regular
    #                                       pixel. Reference pixel are usually
    #                                       a little lower noise.
    #         ktc_noise   - kTC noise in electrons. Set this equal to
    #                       sqrt(k*T*C_pixel)/q_e,  where k is Boltzmann's
    #                       constant,  T is detector temperature,  and C_pixel is
    #                       pixel capacitance. For an H2RG,  the pixel capacitance
    #                       is typically about 40 fF.
    #         bias_offset - On average,  integrations start here in electrons. Set
    #                       this so that all pixel are in range.
    #         bias_amp    - A multiplicative factor that we multiply PCA-zero by
    #                       to simulate a bias pattern. This is completely
    #                       independent from adding in "picture frame" noise.
    #
    #         pedestal - NOT IMPLEMENTED! Magnitude of pedestal drift in electrons
    #
    #     Note1:
    #     Because of the noise correlations,  there is no simple way to
    #     predict the noise of the simulated images. However,  to a
    #     crude first approximation,  these components add in
    #     quadrature.
    #
    #     Note2:
    #     The units in the above are mostly "electrons". This follows convention
    #     in the astronomical community. From a physics perspective,  holes are
    #     actually the physical entity that is collected in Teledyne's p-on-n
    #     (p-type implants in n-type bulk) HgCdTe architecture.
    #
    #     :param rd_noise:
    #     :param c_pink:
    #     :param u_pink:
    #     :param acn:
    #     :param pca0_amp:
    #     :param reference_pixel_noise_ratio:
    #     :param ktc_noise:
    #     :param bias_offset:
    #     :param bias_amp:
    #     :return:
    #     """
    #
    #     self.message('Starting make_noise()')

    # ======================================================================
    #
    # DEFAULT NOISE PARAMETERS
    #
    # These defaults create noise similar to that seen in the JWST NIRSpec.
    #
    # ======================================================================
    # if rd_noise is None:
    #     rd_noise = 5.2
    # # if pedestal is None:
    # #     pedestal = 4
    # if c_pink is None:
    #     c_pink = 3
    # if u_pink is None:
    #     u_pink = 1
    # if acn is None:
    #     acn = 0.5
    # if pca0_amp is None:
    #     pca0_amp = 0.2

    # Change this only if you know that your detector is different from a
    # typical H2RG.
    # if reference_pixel_noise_ratio is None:
    #     reference_pixel_noise_ratio = 0.8

    # These are used only when generating cubes. They are
    # completely removed when the data are calibrated to
    # correlated double sampling or slope images. We include
    # them in here to make more realistic looking raw cubes.
    # if ktc_noise is None:
    #     ktc_noise = 29.
    # if bias_offset is None:
    #     bias_offset = 5000.
    # if bias_amp is None:
    #     bias_amp = 500.

    # ======================================================================

    # Initialize the result cube. For up-the-ramp integrations,
    # we also add a bias pattern. Otherwise,  we assume
    # that the aim was to simulate a two dimensional correlated
    # double sampling image or slope image.
    # self.message('Initializing results cube')
    # result = np.zeros((self.naxis3,  self.naxis2,  self.naxis1), dtype=np.float32)

    def add_ktc_bias_noise(
        self,
        ktc_noise: float = 29.0,
        bias_offset: float = 5000.0,
        bias_amp: float = 500.0,
    ) -> np.ndarray:
        """TBW.

        Inject a bias pattern and kTC noise.
        :param ktc_noise:
        :param bias_amp:
        :param bias_offset:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if (
            self.time_step > 1
        ):  # NOTE: there is no kTc or Bias noise added for first/single frame
            self._log.debug("Generating ktc_bias_noise")
            # If there are no reference pixel,
            # we know that we are dealing with a subarray. In this case,  we do not
            # inject any bias pattern for now.
            # if self.reference_pixel_border_width > 0:
            #    bias_pattern = self.pca0*bias_amp + bias_offset
            # else:
            #    bias_pattern = bias_offset

            # Always inject bias pattern. Works for WINDOW and STRIPE (JML)
            bias_pattern = self.pca0 * bias_amp + bias_offset

            # Add in some kTC noise. Since this should always come out
            # in calibration,  we do not attempt to model it in detail.
            bias_pattern += ktc_noise * np.random.standard_normal(
                (self.naxis2, self.naxis1)
            )

            # Ensure that there are no negative pixel values. Data cubes
            # are converted to unsigned integer before writing.
            # bias_pattern = np.where(bias_pattern < 0,  0,  bias_pattern)
            # Updated to conform to Python >=2.6. (JML)
            # bias_pattern[bias_pattern < 0] = 0
            # Actually,  I think this makes the most sense to do at the very end (JML)

            # Add in the bias pattern
            for z in np.arange(self.naxis3):
                result[z, :, :] += bias_pattern

        return result

    def add_white_read_noise(
        self, rd_noise: float = 5.2, reference_pixel_noise_ratio: float = 0.8
    ) -> np.ndarray:
        """TBW.

        Make white read noise. This is the same for all pixel.

        :param rd_noise:
        :param reference_pixel_noise_ratio:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if rd_noise > 0:
            self._log.debug("Generating rd_noise")
            w = self.ref_all
            r = reference_pixel_noise_ratio  # Easier to work with
            for z in np.arange(self.naxis3):
                here = np.zeros((self.naxis2, self.naxis1))

                # Noisy reference pixel for each side of detector
                if w[0] > 0:  # lower
                    here[: w[0], :] = (  # noqa: E203
                        r * rd_noise * np.random.standard_normal((w[0], self.naxis1))
                    )
                if w[1] > 0:  # upper
                    here[-w[1] :, :] = (  # noqa: E203
                        r * rd_noise * np.random.standard_normal((w[1], self.naxis1))
                    )
                if w[2] > 0:  # left
                    here[:, : w[2]] = (
                        r * rd_noise * np.random.standard_normal((self.naxis2, w[2]))
                    )
                if w[3] > 0:  # right
                    here[:, -w[3] :] = (  # noqa: E203
                        r * rd_noise * np.random.standard_normal((self.naxis2, w[3]))
                    )

                # Noisy regular pixel
                if np.sum(w) > 0:  # Ref. pixel exist in frame
                    start_y_idx = w[0]
                    end_y_idx = self.naxis2 - w[1]

                    start_x_idx = w[2]
                    end_x_idx = self.naxis1 - w[3]

                    here[
                        start_y_idx:end_y_idx, start_x_idx:end_x_idx
                    ] = rd_noise * np.random.standard_normal(
                        (self.naxis2 - w[0] - w[1], self.naxis1 - w[2] - w[3])
                    )
                else:  # No Ref. pixel,  so add only regular pixel
                    here = rd_noise * np.random.standard_normal(
                        (self.naxis2, self.naxis1)
                    )

                # Add the noise in to the result
                result[z, :, :] += here

        return result

    def add_corr_pink_noise(self, c_pink: float = 3.0) -> np.ndarray:
        """TBW.

        Add correlated pink noise.
        :param c_pink:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if c_pink > 0:
            self._log.debug("Adding c_pink noise")
            tt = c_pink * self.pink_noise("pink")  # tt is a temp. variable
            tt = np.reshape(
                tt, (self.time_step, self.naxis2 + self.nfoh, self.xsize + self.nroh)
            )[:, : self.naxis2, : self.xsize]
            tt = tt[-1, :, :]
            for op in np.arange(self.n_out):
                wind_x0 = op * self.xsize
                x1 = wind_x0 + self.xsize
                # By default fast-scan readout direction is [-->, <--, -->, <--]
                # If reverse_scan_direction is True,  then [<--, -->, <--, -->]
                # Would be nice to include option for all --> or all <--
                if self.reverse_scan_direction:
                    mod_num = 1
                else:
                    mod_num = 0
                if np.mod(op, 2) == mod_num:
                    result[:, :, wind_x0:x1] += tt
                else:
                    result[:, :, wind_x0:x1] += tt[:, :, ::-1]

        return result

    def add_uncorr_pink_noise(self, u_pink: float = 1.0) -> np.ndarray:
        """TBW.

        Add uncorrelated pink noise. Because this pink noise is stationary and
        different for each output,  we don't need to flip it.
        :param u_pink:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if u_pink > 0:
            self._log.debug("Adding u_pink noise")
            for op in np.arange(self.n_out):
                wind_x0 = op * self.xsize
                x1 = wind_x0 + self.xsize
                tt = u_pink * self.pink_noise("pink")
                tt = np.reshape(
                    tt,
                    (self.time_step, self.naxis2 + self.nfoh, self.xsize + self.nroh),
                )[:, : self.naxis2, : self.xsize]
                tt = tt[-1, :, :]
                result[:, :, wind_x0:x1] += tt

        return result

    def add_acn_noise(self, acn: float = 0.5) -> np.ndarray:
        """TBW.

        Add Alternating Column Noise (ACN)
        :param acn:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if acn > 0:
            self._log.debug("Adding acn noise")
            for op in np.arange(self.n_out):
                # Generate new pink noise for each even and odd vector.
                # We give these the abstract names 'a' and 'b' so that we
                # can use a previously worked out formula to turn them
                # back into an image section.
                a = acn * self.pink_noise("acn")
                b = acn * self.pink_noise("acn")

                # Pick out just the real pixel (i.e. ignore the gaps)
                a = a[np.where(self.m_short == 1)]
                b = b[np.where(self.m_short == 1)]

                half_ch_pixels = self.naxis1 * self.naxis2 // (2 * self.n_out)
                if len(a) != half_ch_pixels:
                    ValueError(
                        "This should not happen: in ACN noise len(a) != number of half ch pixel"
                    )
                    # a = np.append(a, np.zeros(halfchpixels-len(a)))
                if len(b) != half_ch_pixels:
                    ValueError(
                        "This should not happen: in ACN noise len(b) != number of half ch pixel"
                    )
                    # b = np.append(b, np.zeros(halfchpixels-len(b)))

                # Reformat into an image section. This uses the formula mentioned above.
                acn_cube = np.reshape(
                    np.transpose(np.vstack((a, b))),
                    (self.naxis3, self.naxis2, self.xsize),
                )

                # Add in the ACN. Because pink noise is stationary,  we can
                # ignore the readout directions. There is no need to flip
                # acn_cube before adding it in.
                wind_x0 = op * self.xsize
                x1 = wind_x0 + self.xsize
                result[:, :, wind_x0:x1] += acn_cube

        return result

    # TODO add pca0_file
    def add_pca_zero_noise(self, pca0_amp: float = 0.2) -> np.ndarray:
        """TBW.

        Add PCA-zero. The PCA-zero template is modulated by 1/f.

        :param pca0_amp:
        :return:
        """
        result = np.zeros((self.naxis3, self.naxis2, self.naxis1), dtype=np.float32)

        if pca0_amp > 0:
            self._log.debug('Adding PCA-zero "picture frame" noise')
            gamma = self.pink_noise(mode="pink")
            zoom_factor = self.naxis2 * self.time_step / np.size(gamma)
            gamma = zoom(gamma, zoom_factor, order=1, mode="mirror")
            gamma = np.reshape(gamma, (self.time_step, self.naxis2))
            gamma = gamma[-1, :]
            # for z in np.arange(self.naxis3):
            for y in np.arange(self.naxis2):
                result[0, y, :] += pca0_amp * self.pca0[y, :] * gamma[y]

        return result

    # TODO: Warning this method modify input parameter 'result' !!
    def format_result(self, result: np.ndarray) -> np.ndarray:
        """TBW.

        If the data cube has only 1 frame,  reformat into a 2-dimensional image.

        :param result:
        :return:
        """
        if self.naxis3 == 1:
            self._log.debug("Reformatting cube into image")
            result = result[0, :, :]

        # If the data cube has more than one frame,  convert to unsigned
        # integer
        if self.naxis3 > 1:
            # Data will be converted to 16-bit unsigned int
            # Ensure that there are no negative pixel values.
            result[result < 0] = 0
            # And that anything higher than 65535 gets tacked to the top end
            result[result >= 2 ** 16] = 2 ** 16 - 1

            # self.message('Converting to 16-bit unsigned integer')
            # result = result.astype('uint16')
            result = result.astype("float64")

        self._log.debug("Exiting make_noise()")

        return result

    def create_hdu(self, result: np.ndarray, o_file: t.Optional[str] = None) -> None:
        """TBW.

        Create HDU file and saving data to it
        :return:
        """
        hdu = fits.PrimaryHDU(result)
        # hdu.header.append()
        # hdu.header.append(('RD_NOISE',  rd_noise,  'Read noise'))
        # # hdu.header.append(('PEDESTAL',  pedestal,  'Pedestal drifts'))
        # hdu.header.append(('C_PINK',  c_pink,  'Correlated pink'))
        # hdu.header.append(('U_PINK',  u_pink,  'Uncorrelated pink'))
        # hdu.header.append(('ACN',  acn,  'Alternating column noise'))
        # hdu.header.append(('PCA0',  pca0_amp, 'PCA zero,  AKA picture frame'))
        # hdu.header['HISTORY'] = 'Created by NGHXRG version ' + str(self.nghxrg_version)

        # Write the result to a FITS file
        if o_file is not None:
            self._log.debug("Writing FITS file")
            hdu.writeto(o_file, clobber="True")
