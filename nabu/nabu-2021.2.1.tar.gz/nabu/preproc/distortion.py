import numpy as np
from scipy.interpolate import interpn
from ..utils import check_supported
from ..estimation.distortion import estimate_flat_distortion

def correct_distortion_interpn(image, coords, bounds_error=False, fill_value=None):
    """
    Correct image distortion with scipy.interpolate.interpn.

    Parameters
    ----------
    image: array
        Distorted image
    coords: array
        Coordinates of the distortion correction to apply, with the shape (Ny, Nx, 2)
    """
    return interpn(
        (np.arange(image.shape[0]), np.arange(image.shape[1])),
        image,
        coords,
        bounds_error=bounds_error,
        fill_value=fill_value,
    )

class DistortionCorrection:
    """
    A class for estimating and correcting image distortion.
    """

    estimation_methods = {
        "fft-correlation": estimate_flat_distortion,
    }
    correction_methods = {
        "interpn": correct_distortion_interpn,
    }

    def __init__(
        self,
        estimation_method="fft-correlation",
        estimation_kwargs=None,
        correction_method="interpn",
        correction_kwargs=None,
    ):
        """
        Initialize a DistortionCorrection object.

        Parameters
        -----------
        estimation_method: str
            Name of the method to use for estimating the distortion
        estimation_kwargs: dict, optional
            Named arguments to pass to the estimation method, in the form of a dictionary.
        correction_method: str
            Name of the method to use for correcting the distortion
        correction_kwargs: dict, optional
            Named arguments to pass to the correction method, in the form of a dictionary.
        """
        self._set_estimator(estimation_method, estimation_kwargs)
        self._set_corrector(correction_method, correction_kwargs)


    def _set_estimator(self, estimation_method, estimation_kwargs):
        check_supported(estimation_method, self.estimation_methods.keys(), "estimation method")
        self.estimator = self.estimation_methods[estimation_method]
        self._estimator_kwargs = estimation_kwargs or {}


    def _set_corrector(self, correction_method, correction_kwargs):
        check_supported(correction_method, self.correction_methods.keys(), "correction method")
        self.corrector = self.correction_methods[correction_method]
        self._corrector_kwargs = correction_kwargs or {}


    def estimate_distortion(self, image, reference_image):
        return self.estimator(image, reference_image, **self._estimator_kwargs)

    estimate = estimate_distortion

    def correct_distortion(self, image, coords):
        image_corrected =  self.corrector(image, coords, **self._corrector_kwargs)
        fill_value = self._corrector_kwargs.get("fill_value", None)
        if fill_value is not None and np.isnan(fill_value):
            mask = np.isnan(image_corrected)
            image_corrected[mask] = image[mask]
        return image_corrected

    correct = correct_distortion

    def estimate_and_correct(self, image, reference_image):
        coords = self.estimate_distortion(image, reference_image)
        image_corrected = self.correct_distortion(image, coords)
        return image_corrected
