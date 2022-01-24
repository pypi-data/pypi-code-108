import numpy as np
try:
    from silx.opencl.processing import EventDescription, OpenclProcessing
    from silx.opencl.convolution import Convolution as CLConvolution
    import pyopencl.array as parray
    from pyopencl.elementwise import ElementwiseKernel
    __have_opencl__ = True
except ImportError:
    __have_opencl__ = False
from .unsharp import UnsharpMask

class OpenclUnsharpMask(UnsharpMask, OpenclProcessing):
    def __init__(self, shape, sigma, coeff, mode="reflect", method="gaussian",
                ctx=None, devicetype="all", platformid=None, deviceid=None,
                block_size=None, memory=None, profile=False):
        """
        NB: For now, this class is designed to use the lowest amount of GPU memory
        as possible. Therefore, the input and output image/volumes are assumed
        to be already on device.
        """
        if not(__have_opencl__):
            raise ImportError("Need silx and pyopencl")
        OpenclProcessing.__init__(
            self, ctx=ctx, devicetype=devicetype,
            platformid=platformid, deviceid=deviceid, block_size=block_size,
            memory=memory, profile=profile
        )
        UnsharpMask.__init__(self, shape, sigma, coeff, mode=mode)
        self._init_convolution()
        self._init_mad_kernel()

    def _init_convolution(self):
        self.convolution = CLConvolution(
            self.shape,
            self._gaussian_kernel,
            mode=self.mode,
            ctx=self.ctx, profile=self.profile,
            extra_options={ # Use the lowest amount of memory
                "allocate_input_array": False,
                "allocate_output_array": False,
                "allocate_tmp_array": True,
                "dont_use_textures": True,
            }
        )

    def _init_mad_kernel(self):
        # parray.Array.mul_add is out of place...
        self.mad_kernel = ElementwiseKernel(
            self.ctx,
            "float* array, float fac, float* other, float otherfac",
            "array[i] = fac * array[i] + otherfac * other[i]",
            name="mul_add"
        )

    def unsharp(self, image, output):
        # For now image and output are assumed to be already allocated on device
        assert isinstance(image, parray.Array)
        assert isinstance(output, parray.Array)
        self.convolution(image, output=output)
        if self.method == "gaussian":
            self.mad_kernel(output, -self.coeff, image, 1. + self.coeff)
        else:
            self.mad_kernel(output, self.coeff, image, 1.)
        return output
