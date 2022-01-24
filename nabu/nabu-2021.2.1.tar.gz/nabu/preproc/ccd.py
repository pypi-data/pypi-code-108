import numpy as np
from ..utils import check_supported, deprecated_class
from scipy.ndimage.filters import median_filter

# COMPAT.
from .flatfield import FlatField as Flatfield_, FlatFieldArrays as FlatFieldArrays_, FlatFieldDataUrls as FlatFieldDataUrls_
FlatField = deprecated_class(
    "preproc.ccd.FlatField was moved to preproc.flatfield.FlatField", do_print=True
)(Flatfield_)
FlatFieldArrays = deprecated_class(
    "preproc.ccd.FlatFieldArrays was moved to preproc.flatfield.FlatFieldArrays", do_print=True
)(FlatFieldArrays_)
FlatFieldDataUrls = deprecated_class(
    "preproc.ccd.FlatFieldDataUrls was moved to preproc.flatfield.FlatFieldDataUrls", do_print=True
)(FlatFieldDataUrls_)
#


class CCDFilter:
    """
    A base class for processings applied on radios.
    It is designed to handle chunks of radios (see the documentation for more
    information on the radios chunk concept).
    """

    _supported_ccd_corrections = ["median_clip"]

    def __init__(
        self,
        radios_shape: tuple,
        correction_type: str = "median_clip",
        median_clip_thresh: float = 0.1,
        abs_diff=False,
        preserve_borders=False,
    ):
        """
        Initialize a CCDCorrection instance.

        Parameters
        -----------
        radios_shape: tuple
            A tuple describing the shape of the radios stack, in the form
            `(n_radios, n_z, n_x)`.
        correction_type: str
            Correction type for radios ("median_clip", "sigma_clip", ...)
        median_clip_thresh: float, optional
            Threshold for the median clipping method.
        abs_diff: boolean
            by default False:  the correction is triggered  when img - median > threshold.
            If equals True:    correction is triggered for abs(img-media) > threshold
        preserve borders: boolean
            by default False:
            If equals True:  the borders (width=1) are not modified.


        Notes
        ------
        A CCD correction is a process (usually filtering) taking place in the
        radios space.
        Available filters:
           - median_clip: if the value of the current pixel exceeds the median
             of adjacent pixels (a 3x3 neighborhood) more than a threshold,
             then this pixel value is set to the median value.
        """
        self._set_radios_shape(radios_shape)
        check_supported(correction_type, self._supported_ccd_corrections, "CCD correction mode")
        self.correction_type = correction_type
        self.median_clip_thresh = median_clip_thresh
        self.abs_diff = abs_diff
        self.preserve_borders = preserve_borders


    def _set_radios_shape(self, radios_shape):
        if len(radios_shape) == 2:
            self.radios_shape = (1,) + radios_shape
        elif len(radios_shape) == 3:
            self.radios_shape = radios_shape
        else:
            raise ValueError("Expected radios to have 2 or 3 dimensions")
        n_radios, n_z, n_x = self.radios_shape
        self.n_radios = n_radios
        self.n_angles = n_radios
        self.shape = (n_z, n_x)

    @staticmethod
    def median_filter(img):
        """
        Perform a median filtering on an image.
        """
        return median_filter(img, (3, 3), mode="reflect")

    def median_clip_mask(self, img, return_medians=False):
        """
        Compute a mask indicating whether a pixel is valid or not, according to
        the median-clip method.

        Parameters
        ----------
        img: numpy.ndarray
            Input image
        return_medians: bool, optional
            Whether to return the median values additionally to the mask.
        """
        median_values = self.median_filter(img)
        if not self.abs_diff:
            invalid_mask = img >= median_values + self.median_clip_thresh
        else:
            invalid_mask = abs(img - median_values) > self.median_clip_thresh

        if return_medians:
            return invalid_mask, median_values
        else:
            return invalid_mask

    def median_clip_correction(self, radio, output=None):
        """
        Compute the median clip correction on one image.

        Parameters
        ----------
        radios: numpy.ndarray, optional
            A radio image.
        output: numpy.ndarray, optional
            Output array
        """
        assert radio.shape == self.shape
        if output is None:
            output = np.copy(radio)
        else:
            output[:] = radio[:]
        invalid_mask, medians = self.median_clip_mask(radio, return_medians=True)

        if self.preserve_borders:
            fixed_border = np.array(radio[[0, 0, -1, -1], [0, -1, 0, -1]])

        output[invalid_mask] = medians[invalid_mask]

        if self.preserve_borders:
            output[[0, 0, -1, -1], [0, -1, 0, -1]] = fixed_border

        return output


# Compat.
CCDCorrection = deprecated_class("CCDCorrection is replaced with CCDFilter", do_print=True)(CCDFilter)


class Log:
    """
    Helper class to take -log(radios)

    Parameters
    -----------
    clip_min: float, optional
        Before taking the logarithm, the values are clipped to this minimum.
    clip_max: float, optional
        Before taking the logarithm, the values are clipped to this maximum.
    """

    def __init__(self, radios_shape, clip_min=None, clip_max=None):
        self.radios_shape = radios_shape
        self.clip_min = clip_min
        self.clip_max = clip_max

    def take_logarithm(self, radios):
        """
        Take the negative logarithm of a radios chunk.
        Processing is done in-place !

        Parameters
        -----------
        radios: array
            Radios chunk.
        """
        if (self.clip_min is not None) or (self.clip_max is not None):
            np.clip(radios, self.clip_min, self.clip_max, out=radios)
            np.log(radios, out=radios)
        else:
            np.log(radios, out=radios)
        radios[:] *= -1
        return radios
