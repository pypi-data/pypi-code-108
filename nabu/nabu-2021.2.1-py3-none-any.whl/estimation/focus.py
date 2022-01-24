import numpy as np

from .alignment import plt
from .cor import CenterOfRotation

class CameraFocus(CenterOfRotation):
    def find_distance(
        self,
        img_stack: np.ndarray,
        img_pos: np.array,
        metric="std",
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
    ):
        """Find the focal distance of the camera system.

        This routine computes the motor position that corresponds to having the
        scintillator on the focal plain of the camera system.

        Parameters
        ----------
        img_stack: numpy.ndarray
            A stack of images at different distances.
        img_pos: numpy.ndarray
            Position of the images along the translation axis
        metric: string, optional
            The property, whose maximize occurs at the focal position.
            Defaults to 'std' (standard deviation).
            All options are: 'std' | 'grad' | 'psd'
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

        Returns
        -------
        focus_pos: float
            Estimated position of the focal plane of the camera system.
        focus_ind: float
            Image index of the estimated position of the focal plane of the camera system (starting from 1!).

        Examples
        --------
        Given the focal stack associated to multiple positions of the camera
        focus motor called `img_stack`, and the associated positions `img_pos`,
        the following code computes the highest focus position:

        >>> focus_calc = alignment.CameraFocus()
        ... focus_pos, focus_ind = focus_calc.find_distance(img_stack, img_pos)

        where `focus_pos` is the corresponding motor position, and `focus_ind`
        is the associated image position (starting from 1).
        """
        self._check_img_stack_size(img_stack, img_pos)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        num_imgs = img_stack.shape[0]
        img_shape = img_stack.shape[-2:]
        roi_yxhw = self._determine_roi(img_shape, roi_yxhw)

        img_stack = self._prepare_image(
            img_stack, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, low_pass=low_pass, high_pass=high_pass,
        )

        img_stds = np.std(img_stack, axis=(-2, -1)) / np.mean(img_stack, axis=(-2, -1))

        # assuming images are equispaced
        focus_step = (img_pos[-1] - img_pos[0]) / (num_imgs - 1)

        img_inds = np.arange(num_imgs)
        (f_vals, f_pos) = self.extract_peak_regions_1d(img_stds, peak_radius=peak_fit_radius, cc_coords=img_inds)
        focus_ind, img_std_max = self.refine_max_position_1d(f_vals, return_vertex_val=True)
        focus_ind += f_pos[1, :]

        focus_pos = img_pos[0] + focus_step * focus_ind
        focus_ind += 1

        if self.verbose:
            self.logger.info(
                "Fitted focus motor position:", focus_pos, "and corresponding image position:", focus_ind,
            )
            f, ax = plt.subplots(1, 1)
            self._add_plot_window(f, ax=ax)
            ax.stem(img_pos, img_stds)
            ax.stem(focus_pos, img_std_max, linefmt="C1-", markerfmt="C1o")
            ax.set_title("Images std")
            plt.show(block=False)

        return focus_pos, focus_ind

    def _check_img_block_size(self, img_shape, regions_number, suggest_new_shape=True):
        img_shape = np.array(img_shape)
        new_shape = img_shape
        if not len(img_shape) == 2:
            raise ValueError(
                "Images need to be square 2-dimensional and with shape multiple of the number of assigned regions.\n"
                " Image shape: %s, regions number: %d" % (img_shape, regions_number)
            )
        if not (img_shape[0] == img_shape[1] and np.all((np.array(img_shape) % regions_number) == 0)):
            new_shape = (img_shape // regions_number) * regions_number
            new_shape = np.fmin(new_shape, new_shape.min())
            message = (
                "Images need to be square 2-dimensional and with shape multiple of the number of assigned regions.\n"
                " Image shape: %s, regions number: %d. Cropping to image shape: %s" % (img_shape, regions_number, new_shape)
            )
            if suggest_new_shape:
                self.logger.info(message)
            else:
                raise ValueError(message)
        return new_shape

    @staticmethod
    def _fit_plane(f_vals):
        f_vals_half_shape = (np.array(f_vals.shape) - 1) / 2

        fy = np.linspace(-f_vals_half_shape[-2], f_vals_half_shape[-2], f_vals.shape[-2])
        fx = np.linspace(-f_vals_half_shape[-1], f_vals_half_shape[-1], f_vals.shape[-1])

        fy, fx = np.meshgrid(fy, fx, indexing="ij")
        coords = np.array([np.ones(f_vals.size), fy.flatten(), fx.flatten()])

        return np.linalg.lstsq(coords.T, f_vals.flatten(), rcond=None)[0], fy, fx

    def find_scintillator_tilt(
        self,
        img_stack: np.ndarray,
        img_pos: np.array,
        regions_number=4,
        metric="std",
        roi_yxhw=None,
        median_filt_shape=None,
        padding_mode=None,
        peak_fit_radius=1,
        high_pass=None,
        low_pass=None,
    ):
        """Finds the scintillator tilt and focal distance of the camera system.

        This routine computes the mounting tilt of the scintillator and the
        motor position that corresponds to having the scintillator on the focal
        plain of the camera system.

        The input is supposed to be a stack of square images, whose sizes are
        multiples of the `regions_number` parameter. If images with a different
        size are passed, this function will crop the images. This also generates
        a warning. To suppress the warning, it is suggested to specify a ROI
        that satisfies those criteria (see examples).

        The computed tilts `tilt_vh` are in unit-length per pixel-size. To
        obtain the tilts it is necessary to divide by the pixel-size:

        >>> tilt_vh_deg = np.rad2deg(np.arctan(tilt_vh / pixel_size))

        The correction to be applied is:

        >>> tilt_corr_vh_deg = - np.rad2deg(np.arctan(tilt_vh / pixel_size))

        The legacy octave macros computed the approximation of these values in radians:

        >>> tilt_corr_vh_rad = - tilt_vh / pixel_size

        Note that `pixel_size` should be in the same unit scale as `img_pos`.

        Parameters
        ----------
        img_stack: numpy.ndarray
            A stack of images at different distances.
        img_pos: numpy.ndarray
            Position of the images along the translation axis
        regions_number: int, optional
            The number of regions to subdivide the image into, along each direction.
            Defaults to 4.
        metric: string, optional
            The property, whose maximize occurs at the focal position.
            Defaults to 'std' (standard deviation).
            All options are: 'std' | 'grad' | 'psd'
        roi_yxhw: (2, ) or (4, ) numpy.ndarray, tuple, or array, optional
            4 elements vector containing: vertical and horizontal coordinates
            of first pixel, plus height and width of the Region of Interest (RoI).
            Or a 2 elements vector containing: plus height and width of the
            centered Region of Interest (RoI).
            Default is None -> auto-suggest correct size.
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

        Returns
        -------
        focus_pos: float
            Estimated position of the focal plane of the camera system.
        focus_ind: float
            Image index of the estimated position of the focal plane of the
            camera system (starting from 1!).
        tilts_vh: tuple(float, float)
            Estimated scintillator tilts in the vertical and horizontal
            direction respectively per unit-length per pixel-size.

        Examples
        --------
        Given the focal stack associated to multiple positions of the camera
        focus motor called `img_stack`, and the associated positions `img_pos`,
        the following code computes the highest focus position:

        >>> focus_calc = alignment.CameraFocus()
        ... focus_pos, focus_ind, tilts_vh = focus_calc.find_scintillator_tilt(img_stack, img_pos)
        ... tilt_corr_vh_deg = - np.rad2deg(np.arctan(tilt_vh / pixel_size))

        or to keep compatibility with the old octave macros:

        >>> tilt_corr_vh_rad = - tilt_vh / pixel_size

        For non square images, or images with sizes that are not multiples of
        the `regions_number` parameter, and no ROI is being passed, this function
        will try to crop the image stack to the correct size.
        If you want to remove the warning message, it is suggested to set a ROI
        like the following:

        >>> regions_number = 4
        ... img_roi = (np.array(img_stack.shape[1:]) // regions_number) * regions_number
        ... img_roi = np.fmin(img_roi, img_roi.min())
        ... focus_calc = alignment.CameraFocus()
        ... focus_pos, focus_ind, tilts_vh = focus_calc.find_scintillator_tilt(
        ...     img_stack, img_pos, roi_yxhw=img_roi, regions_number=regions_number)
        """
        self._check_img_stack_size(img_stack, img_pos)

        if peak_fit_radius < 1:
            self.logger.warning("Parameter peak_fit_radius should be at least 1, given: %d instead." % peak_fit_radius)
            peak_fit_radius = 1

        num_imgs = img_stack.shape[0]
        img_shape = img_stack.shape[-2:]
        if roi_yxhw is None:
            # If no roi is being passed, we try to crop the images to the
            # correct size, if needed
            roi_yxhw = self._check_img_block_size(img_shape, regions_number, suggest_new_shape=True)
            roi_yxhw = self._determine_roi(img_shape, roi_yxhw)
        else:
            # If a roi is being passed, and the images don't have the correct
            # shape, we raise an error
            roi_yxhw = self._determine_roi(img_shape, roi_yxhw)
            self._check_img_block_size(roi_yxhw[2:], regions_number, suggest_new_shape=False)

        img_stack = self._prepare_image(
            img_stack, roi_yxhw=roi_yxhw, median_filt_shape=median_filt_shape, low_pass=low_pass, high_pass=high_pass,
        )
        img_shape = img_stack.shape[-2:]

        block_size = np.array(img_shape) / regions_number
        block_stack_size = np.array([num_imgs, regions_number, block_size[-2], regions_number, block_size[-1]], dtype=np.intp,)
        img_stack = np.reshape(img_stack, block_stack_size)

        img_stds = np.std(img_stack, axis=(-3, -1)) / np.mean(img_stack, axis=(-3, -1))
        img_stds = np.reshape(img_stds, [num_imgs, -1]).transpose()

        # assuming images are equispaced
        focus_step = (img_pos[-1] - img_pos[0]) / (num_imgs - 1)

        img_inds = np.arange(num_imgs)
        (f_vals, f_pos) = self.extract_peak_regions_1d(img_stds, peak_radius=peak_fit_radius, cc_coords=img_inds)
        focus_inds = self.refine_max_position_1d(f_vals)
        focus_inds += f_pos[1, :]

        focus_poss = img_pos[0] + focus_step * focus_inds

        # Fitting the plane
        focus_poss = np.reshape(focus_poss, [regions_number, regions_number])
        coeffs, fy, fx = self._fit_plane(focus_poss)
        focus_pos, tg_v, tg_h = coeffs

        # The angular coefficient along x is the tilt around the y axis and vice-versa
        tilts_vh = np.array([tg_h, tg_v]) / block_size

        focus_ind = np.mean(focus_inds) + 1

        if self.verbose:
            self.logger.info(
                "Fitted focus motor position:", focus_pos, "and corresponding image position:", focus_ind,
            )
            self.logger.info("Fitted tilts (to be divided by pixel size, and converted to deg): (v, h) %s" % tilts_vh)
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
            self._add_plot_window(fig, ax=ax)
            ax.plot_wireframe(fx, fy, focus_poss)
            regions_half_shape = (regions_number - 1) / 2
            base_points = np.linspace(-regions_half_shape, regions_half_shape, regions_number)
            ax.plot(
                np.zeros((regions_number,)), base_points, np.polyval([tg_v, focus_pos], base_points), "C2",
            )
            ax.plot(
                base_points, np.zeros((regions_number,)), np.polyval([tg_h, focus_pos], base_points), "C2",
            )
            ax.scatter(0, 0, focus_pos, marker="o", c="C1")
            ax.set_title("Images std")
            plt.show(block=False)

        return focus_pos, focus_ind, tilts_vh
