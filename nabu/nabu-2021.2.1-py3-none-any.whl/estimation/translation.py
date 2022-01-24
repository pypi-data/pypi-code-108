import numpy as np
from numpy.polynomial.polynomial import Polynomial, polyval
from .alignment import AlignmentBase, plt

class DetectorTranslationAlongBeam(AlignmentBase):
    def find_shift(
        self,
        img_stack: np.ndarray,
        img_pos: np.array,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_shifts=False,
        use_adjacent_imgs=False,
    ):
        """Find the vertical and horizontal shifts for translations of the
        detector along the beam direction.

        These shifts are in pixels-per-unit-translation, and they are due to
        the misalignment of the translation stage, with respect to the beam
        propagation direction.

        To compute the vertical and horizontal tilt angles from the obtained `shift_pix`:

        >>> tilt_deg = np.rad2deg(np.arctan(shift_pix * pixel_size))

        where `pixel_size` and and the input parameter `img_pos` have to be
        expressed in the same units.

        Parameters
        ----------
        img_stack: numpy.ndarray
            A stack of images (usually 4) at different distances
        img_pos: numpy.ndarray
            Position of the images along the translation axis
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
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`.
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`.
        return_shifts: boolean, optional
            Adds a third returned argument, containing the pixel shifts of each
            image with respect to the first one in the stack. Defaults to False.
        use_adjacent_imgs: boolean, optional
            Compute correlation between adjacent images.
            It can be used when dealing with large shifts, to avoid overflowing the shift.
            This option allows to replicate the behavior of the reference function `alignxc.m`
            However, it is detrimental to shift fitting accuracy. Defaults to False.

        Returns
        -------
        coeff_v: float
            Estimated vertical shift in pixel per unit-distance of the detector translation.
        coeff_h: float
            Estimated horizontal shift in pixel per unit-distance of the detector translation.
        shifts_vh: list, optional
            The pixel shifts of each image with respect to the first image in the stack.
            Activated if return_shifts is True.

        Examples
        --------
        The following example creates a stack of shifted images, and retrieves the computed shift.
        Here we use a high-pass filter, due to the presence of some low-frequency noise component.

        >>> import numpy as np
        ... import scipy as sp
        ... import scipy.ndimage
        ... from nabu.preproc.alignment import  DetectorTranslationAlongBeam
        ...
        ... tr_calc = DetectorTranslationAlongBeam()
        ...
        ... stack = np.zeros([4, 512, 512])
        ...
        ... # Add low frequency spurious component
        ... for i in range(4):
        ...     stack[i, 200 - i * 10, 200 - i * 10] = 1
        ... stack = sp.ndimage.filters.gaussian_filter(stack, [0, 10, 10.0]) * 100
        ...
        ... # Add the feature
        ... x, y = np.meshgrid(np.arange(stack.shape[-1]), np.arange(stack.shape[-2]))
        ... for i in range(4):
        ...     xc = x - (250 + i * 1.234)
        ...     yc = y - (250 + i * 1.234 * 2)
        ...     stack[i] += np.exp(-(xc * xc + yc * yc) * 0.5)
        ...
        ... # Image translation along the beam
        ... img_pos = np.arange(4)
        ...
        ... # Find the shifts from the features
        ... shifts_v, shifts_h = tr_calc.find_shift(stack, img_pos, high_pass=1.0)
        ... print(shifts_v, shifts_h)
        >>> ( -2.47 , -1.236 )

        and the following commands convert the shifts in angular tilts:

        >>> tilt_v_deg = np.rad2deg(np.arctan(shifts_v * pixel_size))
        >>> tilt_h_deg = np.rad2deg(np.arctan(shifts_h * pixel_size))

        To enable the legacy behavior of `alignxc.m` (correlation between adjacent images):

        >>> shifts_v, shifts_h = tr_calc.find_shift(stack, img_pos, use_adjacent_imgs=True)

        To plot the correlation shifts and the fitted straight lines for both directions:

        >>> tr_calc = DetectorTranslationAlongBeam(verbose=True)
        ... shifts_v, shifts_h = tr_calc.find_shift(stack, img_pos)
        """
        self._check_img_stack_size(img_stack, img_pos)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        num_imgs = img_stack.shape[0]
        img_shape = img_stack.shape[-2:]
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_stack = self._prepare_image(img_stack, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        # do correlations
        ccs = [
            self._compute_correlation_fft(
                img_stack[ii - 1 if use_adjacent_imgs else 0, ...],
                img_stack[ii, ...],
                padding_mode,
                high_pass=high_pass,
                low_pass=low_pass,
            )
            for ii in range(1, num_imgs)
        ]

        img_shape = img_stack.shape[-2:]
        cc_vs = np.fft.fftfreq(img_shape[-2], 1 / img_shape[-2])
        cc_hs = np.fft.fftfreq(img_shape[-1], 1 / img_shape[-1])

        shifts_vh = np.zeros((num_imgs, 2))
        for ii, cc in enumerate(ccs):
            (f_vals, fv, fh) = self.extract_peak_region_2d(cc, peak_radius=peak_fit_radius, cc_vs=cc_vs, cc_hs=cc_hs)
            shifts_vh[ii + 1, :] = self.refine_max_position_2d(f_vals, fv, fh)

        if use_adjacent_imgs:
            shifts_vh = np.cumsum(shifts_vh, axis=0)

        # Polynomial.fit is supposed to be more numerically stable than polyfit
        # (according to numpy)
        coeffs_v = Polynomial.fit(img_pos, shifts_vh[:, 0], deg=1).convert().coef
        coeffs_h = Polynomial.fit(img_pos, shifts_vh[:, 1], deg=1).convert().coef

        if self.verbose:
            self.logger.info("Fitted pixel shifts per unit-length: vertical = %f, horizontal = %f" % (coeffs_v[1], coeffs_h[1]))
            f, axs = plt.subplots(1, 2)
            self._add_plot_window(f, ax=axs)
            axs[0].scatter(img_pos, shifts_vh[:, 0])
            axs[0].plot(img_pos, polyval(img_pos, coeffs_v), "-C1")
            axs[0].set_title("Vertical shifts")
            axs[1].scatter(img_pos, shifts_vh[:, 1])
            axs[1].plot(img_pos, polyval(img_pos, coeffs_h), "-C1")
            axs[1].set_title("Horizontal shifts")
            plt.show(block=False)

        if return_shifts:
            return coeffs_v[1], coeffs_h[1], shifts_vh
        else:
            return coeffs_v[1], coeffs_h[1]

