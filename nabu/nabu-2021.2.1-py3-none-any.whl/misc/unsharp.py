import numpy as np
from scipy.ndimage import convolve1d
from silx.image.utils import gaussian_kernel

class UnsharpMask:
    """
    A helper class for unsharp masking.
    """

    avail_methods = ["gaussian", "log"]

    def __init__(self, shape, sigma, coeff, mode="reflect", method="gaussian"):
        """
        Initialize a Unsharp mask.
        `UnsharpedImage =  (1 + coeff)*Image - coeff * ConvolutedImage`

        If method == "log":
        `UnsharpedImage = Image + coeff*ConvolutedImage`

        Parameters
        -----------
        shape: tuple
            Shape of the image.
        sigma: float
            Standard deviation of the Gaussian kernel
        coeff: float
            Coefficient in the linear combination of unsharp mask
        mode: str, optional
            Convolution mode. Default is "reflect"
        method: str, optional
            Method of unsharp mask. Can be "gaussian" (default) or "log" for
            Laplacian of Gaussian.
        """
        self.shape = shape
        self.ndim = len(self.shape)
        self.sigma = sigma
        self.coeff = coeff
        self._set_method(method)
        self.mode = mode
        self._compute_gaussian_kernel()

    def _set_method(self, method):
        if method not in self.avail_methods:
            raise ValueError(
                "Unknown unsharp method '%s'. Available are %s"
                % (method, str(self.avail_methods))
            )
        self.method = method

    def _compute_gaussian_kernel(self):
        self._gaussian_kernel = np.ascontiguousarray(gaussian_kernel(self.sigma), dtype=np.float32)

    def _blur2d(self, image):
        res1 = convolve1d(image, self._gaussian_kernel, axis=1, mode=self.mode)
        res = convolve1d(res1, self._gaussian_kernel, axis=0, mode=self.mode)
        return res

    def unsharp(self, image, output=None):
        """
        Reference unsharp mask implementation.
        """
        image_b = self._blur2d(image)
        if self.method == "gaussian":
            res = (1 + self.coeff) * image - self.coeff * image_b
        else: # LoG
            res = image + self.coeff * image_b
        if output is not None:
            output[:] = res[:]
            return output
        return res
