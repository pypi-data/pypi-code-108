import numpy as np
from ..utils import get_cuda_srcfile, updiv, check_supported
from .kernel import CudaKernel
from .processing import CudaProcessing
import pycuda.gpuarray as garray


class CudaPadding:
    """
    A class for performing padding on GPU
    """
    supported_modes = ["constant", "edge", "reflect", "symmetric", "wrap"]

    def __init__(self, shape, pad_width, mode="constant", cuda_options=None, **kwargs):
        """
        Initialize a CudaPadding object.

        Parameters
        ----------
        shape: tuple
            Image shape
        pad_width: tuple
            Padding width for each axis. Please see the documentation of numpy.pad().
            It can also be a tuple of two numpy arrays for generic coordinate transform.
        mode: str
            Padding mode

        Other parameters
        ----------------
        constant_values: tuple
            Tuple containing the values to fill when mode="constant".
        """
        if len(shape) != 2:
            raise ValueError("This class only works on images")
        self.shape = shape
        self._set_mode(mode, **kwargs)
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        self._get_padding_arrays(pad_width)
        self._init_cuda_coordinate_transform()


    def _set_mode(self, mode, **kwargs):
        if mode == "edges":
            mode = "edge"
        check_supported(mode, self.supported_modes, "padding mode")
        self.mode = mode
        self._kwargs = kwargs


    def _get_padding_arrays(self, pad_width):
        self.pad_width = pad_width
        if isinstance(pad_width, tuple) and isinstance(pad_width[0], np.ndarray):
            # user-defined coordinate transform
            if len(pad_width) != 2:
                raise ValueError(
                    "pad_width must be either a scalar, a tuple in the form ((a, b), (c, d)), or a tuple of two numpy arrays"
                )
            if self.mode == "constant":
                raise ValueError("Custom coordinate transform does not work with mode='constant'")
            self.mode = "custom"
            self.coords_rows, self.coords_cols = pad_width
        else:
            if self.mode == "constant":
                # no need for coordinate transform here
                constant_values = self._kwargs.get("constant_values", 0)
                self.padded_array_constant = np.pad(
                    np.zeros(self.shape, dtype="f"),
                    self.pad_width,
                    mode="constant",
                    constant_values=constant_values
                )
                self.padded_shape = self.padded_array_constant.shape
                return
            R, C = np.indices(self.shape, dtype=np.int32)
            self.coords_rows = np.pad(R, self.pad_width, mode=self.mode)
            self.coords_cols = np.pad(C, self.pad_width, mode=self.mode)
        self.padded_shape = self.coords_rows.shape


    def _init_cuda_coordinate_transform(self):
        if self.mode == "constant":
            self.d_padded_array_constant = garray.to_gpu(self.padded_array_constant)
            return
        self._coords_transform_kernel = CudaKernel(
            "coordinate_transform",
            filename=get_cuda_srcfile("padding.cu"),
            signature="PPPPiii",
        )
        self._coords_transform_block = (32, 32, 1)
        self._coords_transform_grid = [
            updiv(a, b)
            for a, b in zip(self.padded_shape[::-1], self._coords_transform_block)
        ]
        self.d_coords_rows = garray.to_gpu(self.coords_rows)
        self.d_coords_cols = garray.to_gpu(self.coords_cols)


    def _pad_constant(self, image, output):
        pad_y, pad_x = self.pad_width
        self.d_padded_array_constant[pad_y[0]:pad_y[0]+self.shape[0], pad_x[0]: pad_x[0] + self.shape[1]] = image[:]
        output[:] = self.d_padded_array_constant[:]
        return output


    def pad(self, image, output=None):
        """
        Pad an array.

        Parameters
        ----------
        image: pycuda.gpuarray.GPUArray
            Image to pad
        output: pycuda.gpuarray.GPUArray, optional
            Output image. If provided, must be in the expected shape.
        """
        if output is None:
            output = self.cuda_processing.allocate_array("d_output", self.padded_shape)
        if self.mode == "constant":
            return self._pad_constant(image, output)
        self._coords_transform_kernel(
            image,
            output,
            self.d_coords_cols,
            self.d_coords_rows,
            np.int32(self.shape[1]),
            np.int32(self.padded_shape[1]),
            np.int32(self.padded_shape[0]),
            grid=self._coords_transform_grid,
            block=self._coords_transform_block
        )
        return output
