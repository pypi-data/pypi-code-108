import numpy as np
from .rotation import Rotation
from ..utils import get_cuda_srcfile, updiv
from ..cuda.utils import __has_pycuda__, copy_array
from ..cuda.processing import CudaProcessing
if __has_pycuda__:
    from ..cuda.kernel import CudaKernel
    import pycuda.gpuarray as garray
    import pycuda.driver as cuda


class CudaRotation(Rotation):
    def __init__(self, shape, angle, center=None, mode="edge", reshape=False, cuda_options=None, **sk_kwargs):
        if center is None:
            center = ((shape[1] - 1)/2., (shape[0] - 1)/2.)
        super().__init__(
            shape, angle,
            center=center, mode=mode, reshape=reshape, **sk_kwargs
        )
        self._init_cuda_rotation(cuda_options)


    def _init_cuda_rotation(self, cuda_options):
        cuda_options = cuda_options or {}
        self.cuda_processing = CudaProcessing(**cuda_options)
        self._allocate_arrays()
        self._init_rotation_kernel()


    def _allocate_arrays(self):
        self._d_image_cua = cuda.np_to_array(np.zeros(self.shape, "f"), "C")
        self.cuda_processing.init_arrays_to_none(["d_output"])


    def _init_rotation_kernel(self):
        self.cuda_rotation_kernel = CudaKernel(
            "rotate",
            get_cuda_srcfile("rotation.cu")
        )
        self.texref_image = self.cuda_rotation_kernel.module.get_texref("tex_image")
        self.texref_image.set_filter_mode(cuda.filter_mode.LINEAR) # bilinear
        self.texref_image.set_address_mode(0, cuda.address_mode.CLAMP) # TODO tune
        self.texref_image.set_address_mode(1, cuda.address_mode.CLAMP) # TODO tune
        self.cuda_rotation_kernel.prepare("Piiffff", [self.texref_image])
        self.texref_image.set_array(self._d_image_cua)
        self._cos_theta = np.cos(np.deg2rad(self.angle))
        self._sin_theta = np.sin(np.deg2rad(self.angle))
        self._Nx = np.int32(self.shape[1])
        self._Ny = np.int32(self.shape[0])
        self._center_x = np.float32(self.center[0])
        self._center_y = np.float32(self.center[1])
        self._block = (32, 32, 1) # tune ?
        self._grid = (
            updiv(self.shape[1], self._block[1]),
            updiv(self.shape[0], self._block[0]),
            1
        )


    def rotate(self, img, output=None, do_checks=True):
        copy_array(self._d_image_cua, img, check=do_checks)
        if output is not None:
            d_out = output
        else:
            self.cuda_processing.allocate_array("d_output", self.shape, np.float32)
            d_out = self.cuda_processing.d_output
        self.cuda_rotation_kernel(
            d_out, self._Nx, self._Ny,
            self._cos_theta, self._sin_theta,
            self._center_x, self._center_y,
            grid=self._grid,
            block=self._block,
        )
        return d_out

    __call__ = rotate
