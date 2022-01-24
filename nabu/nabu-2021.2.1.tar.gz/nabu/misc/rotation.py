import numpy as np

try:
    from skimage.transform import rotate
    __have__skimage__ = True
except ImportError:
    __have__skimage__ = False


class Rotation:

    supported_modes = {
        "constant": "constant",
        "zeros": "constant",
        "edge": "edge",
        "edges": "edge",
        "symmetric": "symmetric",
        "sym": "symmetric",
        "reflect": "reflect",
        "wrap": "wrap",
        "periodic": "wrap",
    }

    def __init__(self, shape, angle, center=None, mode="edge", reshape=False, **sk_kwargs):
        """
        Initiate a Rotation object.

        Parameters
        ----------
        shape: tuple of int
            Shape of the images to process
        angle: float
            Rotation angle in DEGREES
        center: tuple of float, optional
            Coordinates of the center of rotation, in the format (X, Y) (mind the non-python
            convention !).
            Default is ((Nx - 1)/2.0, (Ny - 1)/2.0)
        mode: str, optional
            Padding mode. Default is "edge".
        reshape: bool, optional


        Other Parameters
        -----------------
        All the other parameters are passed directly to scikit image 'rotate' function:
        order, cval, clip, preserve_range.
        """
        self.shape = shape
        self.angle = angle
        self.center = center
        self.mode = mode
        self.reshape = reshape
        self.sk_kwargs = sk_kwargs


    def rotate(self, img, output=None):
        if not __have__skimage__:
            raise ValueError("scikit-image is needed for using rotate()")
        res = rotate(
            img, self.angle,
            resize=self.reshape,
            center=self.center,
            mode=self.mode,
            **self.sk_kwargs
        )
        if output is not None:
            output[:] = res[:]
            return output
        else:
            return res


    __call__ = rotate
