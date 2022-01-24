import numpy as np
from numpy.polynomial.polynomial import Polynomial, polyval
from .alignment import median_filter, plt
from .cor import CenterOfRotation
try:
    import skimage.transform as skt
    __have_skimage__ = True
except ImportError:
    __have_skimage__ = False

class CameraTilt(CenterOfRotation):
    def compute_angle(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        method="1d-correlation",
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
    ):
        """Find the camera tilt, given two opposite images.

        This method finds the tilt between the camera pixel columns and the
        rotation axis, by performing a 1-dimensional correlation between two
        opposite images.

        The output of this function, allows to compute motor movements for
        aligning the camera tilt.

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        method: str
            Tilt angle computation method. Default is "1d-correlation" (traditional).
            All options are:
              - "1d-correlation": fastest, but works best for small tilts
              - "fft-polar": slower, but works well on all ranges of tilts
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> deactivated.
        median_filt_shape: (2, ) numpy.ndarray, tuple, or array, optional
            Shape of the median filter window. Default is None -> deactivated.
        padding_mode: str in numpy.pad's mode list, optional
            Padding mode, which determines the type of convolution. If None or
            'wrap' are passed, this resorts to the traditional circular convolution.
            If 'edge' or 'constant' are passed, it results in a linear convolution.
            Default is the circular convolution.
            All options are:
                None | 'constant' | 'edge' | 'linear_ramp' | 'maximum' | 'mean'
                | 'median' | 'minimum' | 'reflect' | 'symmetric' |'wrap'
        peak_fit_radius: int, optional
            Radius size around the max correlation pixel, for sub-pixel fitting.
            Minimum and default value is 1.
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`

        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        cor_offset_pix: float
            Estimated center of rotation position from the center of the RoI in pixels.
        tilt_deg: float
            Estimated camera tilt angle in degrees.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... tilt_calc = CameraTilt()
        ... cor_offset, camera_tilt = tilt_calc.compute_angle(radio1, radio2)

        Or for noisy images:

        >>> cor_offset, camera_tilt = tilt_calc.compute_angle(radio1, radio2, median_filt_shape=(3, 3))
        """
        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        if method.lower() == "1d-correlation":
            return self._compute_angle_1dcorrelation(
                img_1, img_2, padding_mode, peak_fit_radius=peak_fit_radius, high_pass=high_pass, low_pass=low_pass)
        elif method.lower() == "fft-polar":
            if not __have_skimage__:
                raise ValueError(
                    "Camera tilt calculation using \"fft-polar\" is only available with scikit-image."
                    " Please install the package to use this option."
                )

            return self._compute_angle_fftpolar(
                img_1, img_2, padding_mode, peak_fit_radius=peak_fit_radius, high_pass=high_pass, low_pass=low_pass)
        else:
            raise ValueError("Invalid method: %s. Valid options are: \"1d-correlation\" | \"fft-polar\"" % method)

    def _compute_angle_1dcorrelation(
        self, img_1: np.ndarray, img_2: np.ndarray, padding_mode=None, peak_fit_radius=1, high_pass=None, low_pass=None
    ):
        cc = self._compute_correlation_fft(img_1, img_2, padding_mode, axes=(-1,), high_pass=high_pass, low_pass=low_pass)

        img_shape = img_2.shape
        cc_h_coords = np.fft.fftfreq(img_shape[-1], 1 / img_shape[-1])

        (f_vals, fh) = self.extract_peak_regions_1d(cc, peak_radius=peak_fit_radius, cc_coords=cc_h_coords)
        fitted_shifts_h = self.refine_max_position_1d(f_vals)
        fitted_shifts_h += fh[1, :]

        # Computing tilt
        fitted_shifts_h = median_filter(fitted_shifts_h, size=3)

        half_img_size = (img_shape[-2] - 1) / 2
        cc_v_coords = np.linspace(-half_img_size, half_img_size, img_shape[-2])
        coeffs_h = Polynomial.fit(cc_v_coords, fitted_shifts_h, deg=1).convert().coef

        tilt_deg = np.rad2deg(-coeffs_h[1] / 2)
        cor_offset_pix = coeffs_h[0] / 2

        if self.verbose:
            self.logger.info(
                "Fitted center of rotation (pixels):", cor_offset_pix, "and camera tilt (degrees):", tilt_deg,
            )
            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.scatter(cc_v_coords, fitted_shifts_h)
            ax.plot(cc_v_coords, polyval(cc_v_coords, coeffs_h), "-C1")
            ax.set_title("Correlation peaks")
            plt.show(block=False)

        return cor_offset_pix, tilt_deg

    def _compute_angle_fftpolar(
        self, img_1: np.ndarray, img_2: np.ndarray, padding_mode=None, peak_fit_radius=1, high_pass=None, low_pass=None
    ):
        img_shape = img_2.shape

        img_fft_1, img_fft_2, filt, _ = self._transform_to_fft(
            img_1, img_2, padding_mode=padding_mode, axes=(-2, -1), low_pass=low_pass, high_pass=high_pass
        )
        if filt is not None:
            img_fft_1 *= filt
            img_fft_2 *= filt

        # abs removes the translation component
        img_fft_1 = np.abs(np.fft.fftshift(img_fft_1, axes=(-2, -1)))
        img_fft_2 = np.abs(np.fft.fftshift(img_fft_2, axes=(-2, -1)))

        # transform to polar coordinates
        img_fft_1 = skt.warp_polar(img_fft_1, scaling="linear", output_shape=img_shape)
        img_fft_2 = skt.warp_polar(img_fft_2, scaling="linear", output_shape=img_shape)

        # only use half of the fft domain
        img_fft_1 = img_fft_1[..., :img_fft_1.shape[-2] // 2, :]
        img_fft_2 = img_fft_2[..., :img_fft_2.shape[-2] // 2, :]

        tilt_pix = self.find_shift(img_fft_1, img_fft_2, shift_axis=-2)
        tilt_deg = -(360 / img_shape[0]) * tilt_pix

        img_1 = skt.rotate(img_1, tilt_deg)
        img_2 = skt.rotate(img_2, -tilt_deg)

        cor_offset_pix = self.find_shift(
            img_1, img_2, padding_mode=padding_mode, peak_fit_radius=peak_fit_radius, high_pass=high_pass, low_pass=low_pass)

        if self.verbose:
            print(
                "Fitted center of rotation (pixels):", cor_offset_pix, "and camera tilt (degrees):", tilt_deg,
            )

        return cor_offset_pix, tilt_deg

