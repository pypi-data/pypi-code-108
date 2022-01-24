# import math
import logging
import numpy as np
from numpy.polynomial.polynomial import Polynomial
from scipy.ndimage.filters import median_filter
import scipy.fft
from ..utils import previouspow2
from ..misc import fourier_filters
from ..resources.logger import LoggerOrPrint
try:
    import matplotlib.pyplot as plt
    __have_matplotlib__ = True
except ImportError:
    logging.getLogger(__name__).warning("Matplotlib not available. Plotting disabled")
    plt = None
    __have_matplotlib__ = False

try:
    from tqdm import tqdm
    def progress_bar(x, verbose=True):
        if verbose:
            return tqdm(x)
        else:
            return x
except ImportError:
    def progress_bar(x, verbose=True):
        return x

local_fftn = scipy.fft.rfftn
local_ifftn = scipy.fft.irfftn

class AlignmentBase:
    def __init__(
        self, vert_fft_width=False, horz_fft_width=False, verbose=False, logger=None, data_type=np.float32,
    ):
        """
        Alignment basic functions.

        Parameters
        ----------
        vert_fft_width: boolean, optional
            If True, restrict the vertical size to a power of 2:

            >>> new_v_dim = 2 ** math.floor(math.log2(v_dim))

        horz_fft_width: boolean, optional
            If True, restrict the horizontal size to a power of 2:

            >>> new_h_dim = 2 ** math.floor(math.log2(h_dim))

        verbose: boolean, optional
            When True it will produce verbose output, including plots.
        data_type: `numpy.float32`
            Computation data type.
        """

        self._init_parameters(vert_fft_width, horz_fft_width, verbose, logger, data_type)
        self._plot_windows = {}

    def _init_parameters(self, vert_fft_width, horz_fft_width, verbose, logger, data_type):
        self.logger = LoggerOrPrint(logger)
        self.truncate_vert_pow2 = vert_fft_width
        self.truncate_horz_pow2 = horz_fft_width

        if verbose and not __have_matplotlib__:
            self.logger.warning("Matplotlib not available. Plotting disabled, despite being activated by user")
            verbose = False
        self.verbose = verbose
        self.data_type = data_type

    @staticmethod
    def _check_img_stack_size(img_stack: np.ndarray, img_pos: np.ndarray):
        shape_stack = np.squeeze(img_stack).shape
        shape_pos = np.squeeze(img_pos).shape
        if not len(shape_stack) == 3:
            raise ValueError(
                "A stack of 2-dimensional images is required. Shape of stack: %s" % (" ".join(("%d" % x for x in shape_stack)))
            )
        if not len(shape_pos) == 1:
            raise ValueError(
                "Positions need to be a 1-dimensional array. Shape of the positions variable: %s"
                % (" ".join(("%d" % x for x in shape_pos)))
            )
        if not shape_stack[0] == shape_pos[0]:
            raise ValueError(
                "The same number of images and positions is required."
                + " Shape of stack: %s, shape of positions variable: %s"
                % (" ".join(("%d" % x for x in shape_stack)), " ".join(("%d" % x for x in shape_pos)),)
            )

    @staticmethod
    def _check_img_pair_sizes(img_1: np.ndarray, img_2: np.ndarray):
        shape_1 = np.squeeze(img_1).shape
        shape_2 = np.squeeze(img_2).shape
        if not len(shape_1) == 2:
            raise ValueError("Images need to be 2-dimensional. Shape of image #1: %s" % (" ".join(("%d" % x for x in shape_1))))
        if not len(shape_2) == 2:
            raise ValueError("Images need to be 2-dimensional. Shape of image #2: %s" % (" ".join(("%d" % x for x in shape_2))))
        if not np.all(shape_1 == shape_2):
            raise ValueError(
                "Images need to be of the same shape. Shape of image #1: %s, image #2: %s"
                % (" ".join(("%d" % x for x in shape_1)), " ".join(("%d" % x for x in shape_2)),)
            )

    @staticmethod
    def refine_max_position_2d(f_vals: np.ndarray, fy=None, fx=None):
        """Computes the sub-pixel max position of the given function sampling.

        Parameters
        ----------
        f_vals: numpy.ndarray
            Function values of the sampled points
        fy: numpy.ndarray, optional
            Vertical coordinates of the sampled points
        fx: numpy.ndarray, optional
            Horizontal coordinates of the sampled points

        Raises
        ------
        ValueError
            In case position and values do not have the same size, or in case
            the fitted maximum is outside the fitting region.

        Returns
        -------
        tuple(float, float)
            Estimated (vertical, horizontal) function max, according to the
            coordinates in fy and fx.
        """
        if not (len(f_vals.shape) == 2):
            raise ValueError(
                "The fitted values should form a 2-dimensional array. Array of shape: [%s] was given."
                % (" ".join(("%d" % s for s in f_vals.shape)))
            )
        if fy is None:
            fy_half_size = (f_vals.shape[0] - 1) / 2
            fy = np.linspace(-fy_half_size, fy_half_size, f_vals.shape[0])
        elif not (len(fy.shape) == 1 and np.all(fy.size == f_vals.shape[0])):
            raise ValueError(
                "Vertical coordinates should have the same length as values matrix. Sizes of fy: %d, f_vals: [%s]"
                % (fy.size, " ".join(("%d" % s for s in f_vals.shape)))
            )
        if fx is None:
            fx_half_size = (f_vals.shape[1] - 1) / 2
            fx = np.linspace(-fx_half_size, fx_half_size, f_vals.shape[1])
        elif not (len(fx.shape) == 1 and np.all(fx.size == f_vals.shape[1])):
            raise ValueError(
                "Horizontal coordinates should have the same length as values matrix. Sizes of fx: %d, f_vals: [%s]"
                % (fx.size, " ".join(("%d" % s for s in f_vals.shape)))
            )

        fy, fx = np.meshgrid(fy, fx, indexing="ij")
        fy = fy.flatten()
        fx = fx.flatten()
        coords = np.array([np.ones(f_vals.size), fy, fx, fy * fx, fy ** 2, fx ** 2])

        coeffs = np.linalg.lstsq(coords.T, f_vals.flatten(), rcond=None)[0]

        # For a 1D parabola `f(x) = ax^2 + bx + c`, the vertex position is:
        # x_v = -b / 2a. For a 2D parabola, the vertex position is:
        # (y, x)_v = - b / A, where:
        A = [[2 * coeffs[4], coeffs[3]], [coeffs[3], 2 * coeffs[5]]]
        b = coeffs[1:3]
        vertex_yx = np.linalg.lstsq(A, -b, rcond=None)[0]

        vertex_min_yx = [np.min(fy), np.min(fx)]
        vertex_max_yx = [np.max(fy), np.max(fx)]
        if np.any(vertex_yx < vertex_min_yx) or np.any(vertex_yx > vertex_max_yx):
            raise ValueError(
                "Fitted (y: {}, x: {}) positions are outside the input margins y: [{}, {}], and x: [{}, {}]".format(
                    vertex_yx[0], vertex_yx[1], vertex_min_yx[0], vertex_max_yx[0], vertex_min_yx[1], vertex_max_yx[1],
                )
            )
        return vertex_yx

    @staticmethod
    def refine_max_position_1d(f_vals, fx=None, return_vertex_val=False):
        """Computes the sub-pixel max position of the given function sampling.

        Parameters
        ----------
        f_vals: numpy.ndarray
            Function values of the sampled points
        fx: numpy.ndarray, optional
            Coordinates of the sampled points
        return_vertex_val: boolean, option
            Enables returning the vertex values. Defaults to False.

        Raises
        ------
        ValueError
            In case position and values do not have the same size, or in case
            the fitted maximum is outside the fitting region.

        Returns
        -------
        float
            Estimated function max, according to the coordinates in fx.
        """
        if not len(f_vals.shape) in (1, 2):
            raise ValueError(
                "The fitted values should be either one or a collection of 1-dimensional arrays. Array of shape: [%s] was given."
                % (" ".join(("%d" % s for s in f_vals.shape)))
            )
        num_vals = f_vals.shape[0]

        if fx is None:
            fx_half_size = (num_vals - 1) / 2
            fx = np.linspace(-fx_half_size, fx_half_size, num_vals)
        else:
            fx = np.squeeze(fx)
            if not (len(fx.shape) == 1 and np.all(fx.size == num_vals)):
                raise ValueError(
                    "Base coordinates should have the same length as values array. Sizes of fx: %d, f_vals: %d"
                    % (fx.size, num_vals)
                )

        if len(f_vals.shape) == 1:
            # using Polynomial.fit, because supposed to be more numerically
            # stable than previous solutions (according to numpy).
            poly = Polynomial.fit(fx, f_vals, deg=2)
            coeffs = poly.convert().coef
        else:
            coords = np.array([np.ones(num_vals), fx, fx ** 2])
            coeffs = np.linalg.lstsq(coords.T, f_vals, rcond=None)[0]

        # For a 1D parabola `f(x) = c + bx + ax^2`, the vertex position is:
        # x_v = -b / 2a.
        vertex_x = -coeffs[1, :] / (2 * coeffs[2, :])

        vertex_min_x = np.min(fx)
        vertex_max_x = np.max(fx)
        lower_bound_ok = vertex_min_x < vertex_x
        upper_bound_ok = vertex_x < vertex_max_x
        if not np.all(lower_bound_ok * upper_bound_ok):
            if len(f_vals.shape) == 1:
                message = "Fitted position {} is outide the input margins [{}, {}]".format(vertex_x, vertex_min_x, vertex_max_x)
            else:
                message = "Fitted positions outide the input margins [{}, {}]: {} below and {} above".format(
                    vertex_min_x, vertex_max_x, np.sum(1 - lower_bound_ok), np.sum(1 - upper_bound_ok),
                )
            raise ValueError(message)
        if return_vertex_val:
            vertex_val = coeffs[0, :] + vertex_x * coeffs[1, :] / 2
            return vertex_x, vertex_val
        else:
            return vertex_x

    @staticmethod
    def extract_peak_region_2d(cc, peak_radius=1, cc_vs=None, cc_hs=None):
        """
        Extracts a region around the maximum value.

        Parameters
        ----------
        cc: numpy.ndarray
            Correlation image.
        peak_radius: int, optional
            The l_inf radius of the area to extract around the peak. The default is 1.
        cc_vs: numpy.ndarray, optional
            The vertical coordinates of `cc`. The default is None.
        cc_hs: numpy.ndarray, optional
            The horizontal coordinates of `cc`. The default is None.

        Returns
        -------
        f_vals: numpy.ndarray
            The extracted function values.
        fv: numpy.ndarray
            The vertical coordinates of the extracted values.
        fh: numpy.ndarray
            The horizontal coordinates of the extracted values.
        """
        img_shape = np.array(cc.shape)
        # get pixel having the maximum value of the correlation array
        pix_max_corr = np.argmax(cc)
        pv, ph = np.unravel_index(pix_max_corr, img_shape)

        # select a n x n neighborhood for the sub-pixel fitting (with wrapping)
        pv = np.arange(pv - peak_radius, pv + peak_radius + 1) % img_shape[-2]
        ph = np.arange(ph - peak_radius, ph + peak_radius + 1) % img_shape[-1]

        # extract the (v, h) pixel coordinates
        fv = None if cc_vs is None else cc_vs[pv]
        fh = None if cc_hs is None else cc_hs[ph]

        # extract the correlation values
        pv, ph = np.meshgrid(pv, ph, indexing="ij")
        f_vals = cc[pv, ph]

        return (f_vals, fv, fh)

    @staticmethod
    def extract_peak_regions_1d(cc, axis=-1, peak_radius=1, cc_coords=None):
        """
        Extracts a region around the maximum value.

        Parameters
        ----------
        cc: numpy.ndarray
            Correlation image.
        axis: int, optional
            Find the max values along the specified direction. The default is -1.
        peak_radius: int, optional
            The l_inf radius of the area to extract around the peak. The default is 1.
        cc_coords: numpy.ndarray, optional
            The coordinates of `cc` along the selected axis. The default is None.

        Returns
        -------
        f_vals: numpy.ndarray
            The extracted function values.
        fc_ax: numpy.ndarray
            The coordinates of the extracted values, along the selected axis.
        """
        if len(cc.shape) == 1:
            cc = cc[None, ...]
        img_shape = np.array(cc.shape)
        if not (len(img_shape) == 2):
            raise ValueError(
                "The input image should be either a 1 or 2-dimensional array. Array of shape: [%s] was given."
                % (" ".join(("%d" % s for s in cc.shape)))
            )
        other_axis = (axis + 1) % 2
        # get pixel having the maximum value of the correlation array
        pix_max = np.argmax(cc, axis=axis)

        # select a n neighborhood for the many 1D sub-pixel fittings (with wrapping)
        p_ax_range = np.arange(-peak_radius, +peak_radius + 1)
        p_ax = (pix_max[None, :] + p_ax_range[:, None]) % img_shape[axis]

        p_ln = np.tile(np.arange(0, img_shape[other_axis])[None, :], [2 * peak_radius + 1, 1])

        # extract the pixel coordinates along the axis
        fc_ax = None if cc_coords is None else cc_coords[p_ax.flatten()].reshape(p_ax.shape)

        # extract the correlation values
        if other_axis == 0:
            f_vals = cc[p_ln, p_ax]
        else:
            f_vals = cc[p_ax, p_ln]

        return (f_vals, fc_ax)

    def _determine_roi(self, img_shape, roi_yxhw):
        if roi_yxhw is None:
            # vertical and horizontal window sizes are reduced to a power of 2
            # to accelerate fft if requested. Default is not.
            roi_yxhw = previouspow2(img_shape)
            if not self.truncate_vert_pow2:
                roi_yxhw[0] = img_shape[0]
            if not self.truncate_horz_pow2:
                roi_yxhw[1] = img_shape[1]

        roi_yxhw = np.array(roi_yxhw, dtype=np.intp)
        if len(roi_yxhw) == 2:  # Convert centered 2-element roi into 4-element
            roi_yxhw = np.concatenate(((img_shape - roi_yxhw) // 2, roi_yxhw))
        return roi_yxhw

    def _prepare_image(
        self, img, invalid_val=1e-5, roi_yxhw=None, median_filt_shape=None, low_pass=None, high_pass=None,
    ):
        """
        Prepare and returns  a cropped  and filtered image, or array of filtered images if the input is an  array of images.

        Parameters
        ----------
        img: numpy.ndarray
            image or stack of images
        invalid_val: float
            value to be used in replacement of nan and inf values
        median_filt_shape: int or sequence of int
            the width or the widths of the median window
        low_pass: float or sequence of two floats
            Low-pass filter properties, as described in `nabu.misc.fourier_filters`
        high_pass: float or sequence of two floats
            High-pass filter properties, as described in `nabu.misc.fourier_filters`

        Returns
        -------
        numpy.array_like
            The computed filter
        """
        img = np.squeeze(img)  # Removes singleton dimensions, but does a shallow copy
        img = np.ascontiguousarray(img, dtype=self.data_type)

        if roi_yxhw is not None:
            img = img[
                ..., roi_yxhw[0] : roi_yxhw[0] + roi_yxhw[2], roi_yxhw[1] : roi_yxhw[1] + roi_yxhw[3],
            ]

        img = img.copy()

        img[np.isnan(img)] = invalid_val
        img[np.isinf(img)] = invalid_val

        if high_pass is not None or low_pass is not None:
            img_filter = fourier_filters.get_bandpass_filter(
                img.shape[-2:],
                cutoff_lowpass=low_pass,
                cutoff_highpass=high_pass,
                use_rfft=True,
                data_type=self.data_type,
            )
            # fft2 and iff2 use axes=(-2, -1) by default
            img = local_ifftn(local_fftn(img, axes=(-2, -1)) * img_filter, axes=(-2, -1)).real

        if median_filt_shape is not None:
            img_shape = img.shape
            # expanding filter shape with ones, to cover the stack of images
            # but disabling inter-image filtering
            median_filt_shape = np.concatenate(
                (np.ones((len(img_shape) - len(median_filt_shape),), dtype=np.intp), median_filt_shape,)
            )
            img = median_filter(img, size=median_filt_shape)
        return img

    def _transform_to_fft(
        self, img_1: np.ndarray, img_2: np.ndarray, padding_mode, axes=(-2, -1), low_pass=None, high_pass=None
    ):
        do_circular_conv = padding_mode is None or padding_mode == "wrap"
        img_shape = img_2.shape
        if not do_circular_conv:
            pad_size = np.ceil(np.array(img_shape) / 2).astype(np.intp)
            pad_array = [(0,)] * len(img_shape)
            for a in axes:
                pad_array[a] = (pad_size[a],)

            img_1 = np.pad(img_1, pad_array, mode=padding_mode)
            img_2 = np.pad(img_2, pad_array, mode=padding_mode)
        else:
            pad_size = None
        img_shape = img_2.shape

        # compute fft's of the 2 images
        img_fft_1 = local_fftn(img_1, axes=axes)
        img_fft_2 = local_fftn(img_2, axes=axes)

        if low_pass is not None or high_pass is not None:
            filt = fourier_filters.get_bandpass_filter(
                img_shape[-2:],
                cutoff_lowpass=low_pass,
                cutoff_highpass=high_pass,
                use_rfft=True,
                data_type=self.data_type,
            )
        else:
            filt = None

        return img_fft_1, img_fft_2, filt, pad_size

    def _compute_correlation_fft(
        self, img_1: np.ndarray, img_2: np.ndarray, padding_mode, axes=(-2, -1), low_pass=None, high_pass=None
    ):
        img_fft_1, img_fft_2, filt, pad_size = self._transform_to_fft(
            img_1, img_2, padding_mode=padding_mode, axes=axes, low_pass=low_pass, high_pass=high_pass
        )

        img_prod = img_fft_1 * np.conjugate(img_fft_2)

        if filt is not None:
            img_prod *= filt

        # inverse fft of the product to get cross_correlation of the 2 images
        cc = np.real(local_ifftn(img_prod, axes=axes))

        if pad_size is not None:
            cc_shape = cc.shape
            cc = np.fft.fftshift(cc, axes=axes)

            slicing = [slice(None)] * len(cc_shape)
            for a in axes:
                slicing[a] = slice(pad_size[a], cc_shape[a] - pad_size[a])
            cc = cc[tuple(slicing)]

            cc = np.fft.ifftshift(cc, axes=axes)

        return cc

    def _add_plot_window(self, fig, ax=None):
        self._plot_windows[fig.number] = {
            "figure": fig,
            "axes": ax
        }

    def close_plot_window(self, n, errors="raise"):
        """
        Close a plot window. Applicable only if the class was instantiated with verbose=True.

        Parameters
        ----------
        n: int
            Figure number to close
        errors: str, optional
            What to do with errors. It can be either "raise", "log" or "ignore".
        """
        if not self.verbose:
            return
        if n not in self._plot_windows:
            msg = "Cannot close plot window number %d: no such window" % n
            if errors == "raise":
                raise ValueError(msg)
            elif errors == "log":
                self.logger.error(msg)
        fig_ax = self._plot_windows.pop(n)
        plt.close(fig_ax["figure"].number) # would also work with the object itself

    def close_last_plot_windows(self, n=1):
        """
        Close the last "n" plot windows.
        Applicable only if the class was instanciated with verbose=True.

        Parameters
        -----------
        n: int, optional
            Integer indicating how many plot windows should be closed.
        """
        figs_nums = sorted(self._plot_windows.keys(), reverse=True)
        n = min(n, len(figs_nums))
        for i in range(n):
            self.close_plot_window(figs_nums[i], errors="ignore")
