import math
import numpy as np
from ..misc import fourier_filters
from .alignment import AlignmentBase, plt, progress_bar, local_fftn, local_ifftn

# three possible  values for the validity check, which can optionally be returned by the find_shifts methods
cor_result_validity =  {
    "unknown": "unknown",
    "sound": "sound",
    "correct": "sound",
    "questionable": "questionable",
}


class CenterOfRotation(AlignmentBase):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        shift_axis: int = -1,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
    ):
        """Find the Center of Rotation (CoR), given two images.

        This method finds the half-shift between two opposite images, by
        means of correlation computed in Fourier space.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        shift_axis: int
            Axis along which we want the shift to be computed. Default is -1 (horizontal).
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
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.


        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotation()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        cc = self._compute_correlation_fft(img_1, img_2, padding_mode, high_pass=high_pass, low_pass=low_pass)
        img_shape = img_2.shape
        cc_vs = np.fft.fftfreq(img_shape[-2], 1 / img_shape[-2])
        cc_hs = np.fft.fftfreq(img_shape[-1], 1 / img_shape[-1])

        (f_vals, fv, fh) = self.extract_peak_region_2d(cc, peak_radius=peak_fit_radius, cc_vs=cc_vs, cc_hs=cc_hs)
        fitted_shifts_vh = self.refine_max_position_2d(f_vals, fv, fh)

        if return_validity:
            return fitted_shifts_vh[shift_axis] / 2.0, cor_result_validity["unknown"]
        else:
            return fitted_shifts_vh[shift_axis] / 2.0


class CenterOfRotationSlidingWindow(CenterOfRotation):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        side,
        window_width=None,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
    ):
        """Semi-automatically find the Center of Rotation (CoR), given two images
        or sinograms. Suitable for half-aquisition scan.

        This method finds the half-shift between two opposite images,  by
        minimizing difference over a moving window.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        side: string
            Expected region of the CoR. Allowed values: 'left', 'center' or 'right'.
        window_width: int, optional
            Width of window that will slide on the other image / part of the
            sinogram. Default is None.
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
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.

        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationSlidingWindow()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        validity_check_result = cor_result_validity["unknown"]

        if side is None:
            raise ValueError("Side should be one of 'left', 'right', or 'center'. 'None' was given instead")

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning(
                "Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius
            )
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(
            img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_2 = self._prepare_image(
            img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_shape = img_2.shape

        if window_width is None:
            if side.lower() == "center":
                window_width = round(img_shape[-1] / 4.0 * 3.0)
            else:
                window_width = round(img_shape[-1] / 10)
        window_shift = window_width // 2
        window_width = window_shift * 2 + 1

        if side.lower() == "right":
            win_2_start = 0
        elif side.lower() == "left":
            win_2_start = img_shape[-1] - window_width
        elif side.lower() == "center":
            win_2_start = img_shape[-1] // 2 - window_shift
        else:
            raise ValueError("Side should be one of 'left', 'right', or 'center'. '%s' was given instead" % side.lower())

        win_2_end = win_2_start + window_width

        # number of pixels where the window will "slide".
        n = img_shape[-1] - window_width
        diffs_mean = np.zeros((n,), dtype=img_1.dtype)
        diffs_std = np.zeros((n,), dtype=img_1.dtype)

        for ii in progress_bar(range(n), verbose=self.verbose):
            win_1_start, win_1_end = ii, ii + window_width
            img_diff = img_1[:, win_1_start:win_1_end] - img_2[:, win_2_start:win_2_end]
            diffs_abs = np.abs(img_diff)
            diffs_mean[ii] = diffs_abs.mean()
            diffs_std[ii] = diffs_abs.std()

        diffs_mean = diffs_mean.min() - diffs_mean
        win_ind_max = np.argmax(diffs_mean)

        diffs_std = diffs_std.min() - diffs_std
        if not win_ind_max == np.argmax(diffs_std):
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]
        else:
            validity_check_result = cor_result_validity["sound"]

        (f_vals, f_pos) = self.extract_peak_regions_1d(diffs_mean, peak_radius=peak_fit_radius)
        win_pos_max, win_val_max = self.refine_max_position_1d(f_vals, return_vertex_val=True)

        cor_h = -(win_2_start - (win_ind_max + win_pos_max)) / 2.0

        if (side.lower() == "right" and win_ind_max == 0) or (side.lower() == "left" and win_ind_max == n):
            self.logger.warning("Sliding window width %d might be too large!" % window_width)

        if self.verbose:
            cor_pos = -(win_2_start - np.arange(n)) / 2.0

            print("Lowest difference window: index=%d, range=[0, %d]" % (win_ind_max, n))
            print("CoR tested for='%s', found at voxel=%g (from center)" % (side, cor_h))

            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.stem(cor_pos, diffs_mean, label="Mean difference")
            ax.stem(cor_h, win_val_max, linefmt="C1-", markerfmt="C1o", label="Best mean difference")
            ax.stem(cor_pos, -diffs_std, linefmt="C2-", markerfmt="C2o", label="Std-dev difference")
            ax.set_title("Window dispersions")
            plt.show(block=False)

        if return_validity:
            return cor_h, validity_check_result
        else:
            return cor_h


class CenterOfRotationGrowingWindow(CenterOfRotation):
    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        side="all",
        min_window_width=11,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
        return_validity=False,
    ):
        """Automatically find the Center of Rotation (CoR), given two images or
        sinograms. Suitable for half-aquisition scan.

        This method finds the half-shift between two opposite images,  by
        minimizing difference over a moving window.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
        side: string, optional
            Expected region of the CoR. Allowed values: 'left', 'center', 'right', or 'all'.
            Default is 'all'.
        min_window_width: int, optional
            Minimum window width that covers the common region of the two images /
            sinograms. Default is 11.
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
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.



        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationGrowingWindow()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3))
        """

        validity_check_result = cor_result_validity["unknown"]

        self._check_img_pair_sizes(img_1, img_2)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        img_shape = img_2.shape
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_1 = self._prepare_image(
            img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_2 = self._prepare_image(
            img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, high_pass=high_pass, low_pass=low_pass
        )
        img_shape = img_2.shape

        def window_bounds(mid_point, window_max_width=img_shape[-1]):
            return (
                np.fmax(np.ceil(mid_point - window_max_width / 2), 0).astype(np.intp),
                np.fmin(np.ceil(mid_point + window_max_width / 2), img_shape[-1]).astype(np.intp),
            )

        img_lower_half_size = np.floor(img_shape[-1] / 2).astype(np.intp)
        img_upper_half_size = np.ceil(img_shape[-1] / 2).astype(np.intp)

        if side.lower() == "right":
            win_1_mid_start = img_lower_half_size
            win_1_mid_end = np.floor(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
            win_2_mid_start = -img_upper_half_size + min_window_width
            win_2_mid_end = img_upper_half_size
        elif side.lower() == "left":
            win_1_mid_start = -img_lower_half_size + min_window_width
            win_1_mid_end = img_lower_half_size
            win_2_mid_start = img_upper_half_size
            win_2_mid_end = np.ceil(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
        elif side.lower() == "center":
            win_1_mid_start = 0
            win_1_mid_end = img_shape[-1]
            win_2_mid_start = 0
            win_2_mid_end = img_shape[-1]
        elif side.lower() == "all":
            win_1_mid_start = -img_lower_half_size + min_window_width
            win_1_mid_end = np.floor(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
            win_2_mid_start = -img_upper_half_size + min_window_width
            win_2_mid_end = np.ceil(img_shape[-1] * 3 / 2).astype(np.intp) - min_window_width
        else:
            raise ValueError("Side should be one of 'left', 'right', or 'center'. '%s' was given instead" % side.lower())

        n1 = win_1_mid_end - win_1_mid_start
        n2 = win_2_mid_end - win_2_mid_start

        if not n1 == n2:
            raise ValueError(
                "Internal error: the number of window steps for the two images should be the same."
                + "Found the following configuration instead => Side: %s, #1: %d, #2: %d" % (side, n1, n2)
            )

        diffs_mean = np.zeros((n1,), dtype=img_1.dtype)
        diffs_std = np.zeros((n1,), dtype=img_1.dtype)

        for ii in progress_bar(range(n1), verbose=self.verbose):
            win_1 = window_bounds(win_1_mid_start + ii)
            win_2 = window_bounds(win_2_mid_end - ii)
            img_diff = img_1[:, win_1[0] : win_1[1]] - img_2[:, win_2[0] : win_2[1]]
            diffs_abs = np.abs(img_diff)
            diffs_mean[ii] = diffs_abs.mean()
            diffs_std[ii] = diffs_abs.std()

        diffs_mean = diffs_mean.min() - diffs_mean
        win_ind_max = np.argmax(diffs_mean)

        diffs_std = diffs_std.min() - diffs_std
        if not win_ind_max == np.argmax(diffs_std):
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]
        else:
            validity_check_result = cor_result_validity["sound"]

        (f_vals, f_pos) = self.extract_peak_regions_1d(diffs_mean, peak_radius=peak_fit_radius)
        win_pos_max, win_val_max = self.refine_max_position_1d(f_vals, return_vertex_val=True)

        cor_h = (win_1_mid_start + (win_ind_max + win_pos_max) - img_upper_half_size) / 2.0

        if (side.lower() == "right" and win_ind_max == 0) or (side.lower() == "left" and win_ind_max == n1):
            self.logger.warning("Minimum growing window width %d might be too large!" % min_window_width)

        if self.verbose:
            cor_pos = (win_1_mid_start + np.arange(n1) - img_upper_half_size) / 2.0

            self.logger.info("Lowest difference window: index=%d, range=[0, %d]" % (win_ind_max, n1))
            self.logger.info("CoR tested for='%s', found at voxel=%g (from center)" % (side, cor_h))

            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.stem(cor_pos, diffs_mean, label="Mean difference")
            ax.stem(cor_h, win_val_max, linefmt="C1-", markerfmt="C1o", label="Best mean difference")
            ax.stem(cor_pos, -diffs_std, linefmt="C2-", markerfmt="C2o", label="Std-dev difference")
            ax.set_title("Window dispersions")
            plt.show(block=False)

        if return_validity:
            return cor_h, validity_check_result
        else:
            return cor_h


class CenterOfRotationAdaptiveSearch(CenterOfRotation):
    """This adaptive method works by applying a gaussian which highlights, by apodisation, a region
    which can possibly contain the good center of rotation.
    The whole image is spanned during several applications of the apodisation. At each application
    the apodisation function, which is a gaussian, is moved to a new guess position.
    The lenght of the step, by which the gaussian is moved, and its sigma are
    obtained by multiplying the shortest distance from the left or right border with
    a self.step_fraction and  self.sigma_fraction factors which ensure global overlapping.
    for each step a region around the CoR  of each image is selected, and the regions of the two images
    are compared to  calculate a cost function. The value of the cost function, at its minimum
    is used to select the best step at which the CoR is taken as final result.
    The option filtered_cost= True (default) triggers the filtering (according to low_pass and high_pass)
    of the two images which are used for he cost function. ( Note: the low_pass and high_pass options
    are used, if given, also without the filtered_cost option, by being passed to the base class
    CenterOfRotation )
    """

    sigma_fraction = 1.0 / 4.0
    step_fraction = 1.0 / 6.0

    def find_shift(
        self,
        img_1: np.ndarray,
        img_2: np.ndarray,
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        high_pass=None,
        low_pass=None,
        margins=None,
        filtered_cost=True,
        return_validity=False,
    ):
        """Find the Center of Rotation (CoR), given two images.

        This method finds the half-shift between two opposite images, by
        means of correlation computed in Fourier space.
        A global search is done on on the detector span (minus a margin) without assuming centered scan conditions.

        The output of this function, allows to compute motor movements for
        aligning the sample rotation axis. Given the following values:

        - L1: distance from source to motor
        - L2: distance from source to detector
        - ps: physical pixel size
        - v: output of this function

        displacement of motor = (L1 / L2 * ps) * v

        Parameters
        ----------
        img_1: numpy.ndarray
            First image
        img_2: numpy.ndarray
            Second image, it needs to have been flipped already (e.g. using numpy.fliplr).
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
        low_pass: float or sequence of two floats.
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`.
        margins:  None or a couple of floats or ints
            if margins is None or in the form of  (margin1,margin2) the search is done between margin1 and  dim_x-1-margin2.
            If left to None then by default (margin1,margin2)  = ( 10, 10 ).
        filtered_cost: boolean.
            True by default. It triggers the use of filtered images in the calculation of the cost function.
        return_validity: a boolean, defaults to false
            if set to True adds a second return value which may have three string values.
            These values are "unknown", "sound", "questionable".
            It will be "uknown" if the  validation method is not implemented
            and it will be "sound" or "questionable" if it is implemented.

        Raises
        ------
        ValueError
            In case images are not 2-dimensional or have different sizes.

        Returns
        -------
        float
            Estimated center of rotation position from the center of the RoI in pixels.

        Examples
        --------
        The following code computes the center of rotation position for two
        given images in a tomography scan, where the second image is taken at
        180 degrees from the first.

        >>> radio1 = data[0, :, :]
        ... radio2 = np.fliplr(data[1, :, :])
        ... CoR_calc = CenterOfRotationAdaptiveSearch()
        ... cor_position = CoR_calc.find_shift(radio1, radio2)

        Or for noisy images:

        >>> cor_position = CoR_calc.find_shift(radio1, radio2, median_filt_shape=(3, 3), high_pass=20, low_pass=1   )
        """

        validity_check_result = cor_result_validity["unknown"]

        self._check_img_pair_sizes(img_1, img_2)

        used_type = img_1.dtype

        roi_yxhw = self._determine_roi(img_1.shape, roi_yxhw)

        if filtered_cost and (low_pass is not None or high_pass is not None):
            img_filter = fourier_filters.get_bandpass_filter(
                img_1.shape[-2:],
                cutoff_lowpass=low_pass,
                cutoff_highpass=high_pass,
                use_rfft=True,
                data_type=self.data_type,
            )
            # fft2 and iff2 use axes=(-2, -1) by default
            img_filtered_1 = local_ifftn(local_fftn(img_1, axes=(-2, -1)) * img_filter, axes=(-2, -1)).real
            img_filtered_2 = local_ifftn(local_fftn(img_2, axes=(-2, -1)) * img_filter, axes=(-2, -1)).real
        else:
            img_filtered_1 = img_1
            img_filtered_2 = img_2

        img_1 = self._prepare_image(img_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_2 = self._prepare_image(img_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        img_filtered_1 = self._prepare_image(img_filtered_1, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)
        img_filtered_2 = self._prepare_image(img_filtered_2, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape)

        dim_radio = img_1.shape[1]

        if margins is None:
            lim_1, lim_2 = 10, dim_radio - 1 - 10
        else:
            lim_1, lim_2 = margins
            lim_2 = dim_radio - 1 - lim_2

        if lim_1 < 1:
            lim_1 = 1
        if lim_2 > dim_radio - 2:
            lim_2 = dim_radio - 2

        if lim_2 <= lim_1:
            message = (
                "Image shape or cropped selection too small for global search."
                + " After removal of the margins the search limits collide."
                + " The cropped size is %d\n" % (dim_radio)
            )
            raise ValueError(message)

        found_centers = []
        x_cor = lim_1
        while x_cor < lim_2:

            tmp_sigma = min((img_1.shape[1] - x_cor), (x_cor),) * self.sigma_fraction

            tmp_x = (np.arange(img_1.shape[1]) - x_cor) / tmp_sigma
            apodis = np.exp(-tmp_x * tmp_x / 2.0)

            x_cor_rel = x_cor - (img_1.shape[1] // 2)

            img_1_apodised = img_1 * apodis

            try:
                cor_position = CenterOfRotation.find_shift(
                    self,
                    img_1_apodised.astype(used_type),
                    img_2.astype(used_type),
                    low_pass=low_pass,
                    high_pass=high_pass,
                    roi_yxhw=roi_yxhw,
                )
            except ValueError as err:
                message = "ValueError from base class CenterOfRotation.find_shift in CenterOfRotationAdaptiveSearch.find_shift  : {err}".format(
                    err=err
                )
                self.logger.warning(message)
                x_cor = min(x_cor + x_cor * self.step_fraction, x_cor + (dim_radio - x_cor) * self.step_fraction)
                continue
            except:
                message = "Unexpected error from base class CenterOfRotation.find_shift in CenterOfRotationAdaptiveSearch.find_shift  : {err}".format(
                    err=err
                )
                self.logger.error(message)
                raise

            p_1 = cor_position * 2
            if cor_position < 0:
                p_2 = img_2.shape[1] + cor_position * 2
            else:
                p_2 = -img_2.shape[1] + cor_position * 2

            if abs(x_cor_rel - p_1 / 2) < abs(x_cor_rel - p_2 / 2):
                cor_position = p_1 / 2
            else:
                cor_position = p_2 / 2

            cor_in_img = img_1.shape[1] // 2 + cor_position
            tmp_sigma = min((img_1.shape[1] - cor_in_img), (cor_in_img),) * self.sigma_fraction

            M1 = int(round(cor_position + img_1.shape[1] // 2)) - int(round(tmp_sigma))
            M2 = int(round(cor_position + img_1.shape[1] // 2)) + int(round(tmp_sigma))

            piece_1 = img_filtered_1[:, M1:M2]
            piece_2 = img_filtered_2[:, img_1.shape[1] - M2 : img_1.shape[1] - M1]

            if piece_1.size and piece_2.size:
                piece_1 = piece_1 - piece_1.mean()
                piece_2 = piece_2 - piece_2.mean()
                energy = np.array(piece_1 * piece_1 + piece_2 * piece_2, "d").sum()
                diff_energy = np.array((piece_1 - piece_2) * (piece_1 - piece_2), "d").sum()
                cost = diff_energy / energy

                if not np.isnan(cost):
                    if tmp_sigma * 2 > abs(x_cor_rel - cor_position):
                        found_centers.append([cost, abs(x_cor_rel - cor_position), cor_position, energy])

            x_cor = min(x_cor + x_cor * self.step_fraction, x_cor + (dim_radio - x_cor) * self.step_fraction)

        if len(found_centers) == 0:
            message = "Unable to find any valid CoR candidate in {my_class}.find_shift ".format(
                my_class=self.__class__.__name__
            )
            raise ValueError(message)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Now build the neigborhood of the minimum as a list of five elements:
        # the minimum in the middle of the two before, and the two after

        filtered_found_centers = []
        for i in range(len(found_centers)):
            if i > 0:
                if abs(found_centers[i][2] - found_centers[i - 1][2]) < 0.5:
                    filtered_found_centers.append(found_centers[i])
                    continue
            if i + 1 < len(found_centers):
                if abs(found_centers[i][2] - found_centers[i + 1][2]) < 0.5:
                    filtered_found_centers.append(found_centers[i])
                    continue

        if len(filtered_found_centers):
            found_centers = filtered_found_centers

        min_choice = min(found_centers)
        index_min_choice = found_centers.index(min_choice)
        min_neighborood = [
            found_centers[i][2] if (i >= 0 and i < len(found_centers)) else math.nan
            for i in range(index_min_choice - 2, index_min_choice + 2 + 1)
        ]

        score_right = 0
        for i_pos in [3, 4]:
            if abs(min_neighborood[i_pos] - min_neighborood[2]) < 0.5:
                score_right += 1
            else:
                break

        score_left = 0
        for i_pos in [1, 0]:
            if abs(min_neighborood[i_pos] - min_neighborood[2]) < 0.5:
                score_left += 1
            else:
                break

        if score_left + score_right >= 2:
            validity_check_result = cor_result_validity["sound"]
        else:
            self.logger.warning(
                "Minimum mean difference and minimum std-dev of differences do not coincide. "
                + "This means that the validity of the found solution might be questionable."
            )
            validity_check_result = cor_result_validity["questionable"]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # An informative message in case one wish to look at how it has gone
        informative_message = " ".join(
            ["CenterOfRotationAdaptiveSearch found this neighborood of the optimal position:"]
            + [str(t) if not math.isnan(t) else "N.A." for t in min_neighborood]
        )
        self.logger.debug(informative_message)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # The return value is the optimum which had been placed in the middle of the neighborood
        cor_position = min_neighborood[2]

        if return_validity:
            return cor_position, validity_check_result
        else:
            return cor_position

    __call__ = find_shift
