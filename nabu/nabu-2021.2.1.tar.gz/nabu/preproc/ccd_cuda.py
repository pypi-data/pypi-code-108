from typing import Union
import numpy as np
from ..preproc.ccd import CCDFilter, Log
from ..cuda.kernel import CudaKernel
from ..cuda.medfilt import MedianFilter
from ..utils import get_cuda_srcfile, updiv, deprecated_class

# COMPAT.
from .flatfield_cuda import (
    CudaFlatField as CudaFlatfield_,
    CudaFlatFieldArrays as CudaFlatFieldArrays_,
    CudaFlatFieldDataUrls as CudaFlatFieldDataUrls_,
)

FlatField = deprecated_class(
    "preproc.ccd_cuda.CudaFlatField was moved to preproc.flatfield_cuda.CudaFlatField", do_print=True
)(CudaFlatfield_)
FlatFieldArrays = deprecated_class(
    "preproc.ccd_cuda.CudaFlatFieldArrays was moved to preproc.flatfield_cuda.CudaFlatFieldArrays", do_print=True
)(CudaFlatFieldArrays_)
FlatFieldDataUrls = deprecated_class(
    "preproc.ccd_cuda.CudaFlatFieldDataUrls was moved to preproc.flatfield_cuda.CudaFlatFieldDataUrls", do_print=True
)(CudaFlatFieldDataUrls_)
#


class CudaCCDFilter(CCDFilter):
    def __init__(
        self,
        radios_shape: tuple,
        correction_type: str = "median_clip",
        median_clip_thresh: float = 0.1,
        abs_diff=False,
        cuda_options: Union[dict, None] = None,
    ):
        """
        Initialize a CudaCCDCorrection instance.
        Please refer to the documentation of CCDCorrection.
        """
        super().__init__(
            radios_shape,
            correction_type=correction_type,
            median_clip_thresh=median_clip_thresh,
        )
        self._set_cuda_options(cuda_options)
        self.cuda_median_filter = None
        if correction_type == "median_clip":
            self.cuda_median_filter = MedianFilter(
                self.shape,
                footprint=(3, 3),
                mode="reflect",
                threshold=median_clip_thresh,
                abs_diff=abs_diff,
                cuda_options={
                    "device_id": self.cuda_options["device_id"],
                    "ctx": self.cuda_options["ctx"],
                    "cleanup_at_exit": self.cuda_options["cleanup_at_exit"],
                }
            )

    def _set_cuda_options(self, user_cuda_options):
        self.cuda_options = {"device_id": None, "ctx": None, "cleanup_at_exit": None}
        if user_cuda_options is None:
            user_cuda_options = {}
        self.cuda_options.update(user_cuda_options)

    def median_clip_correction(self, radio, output=None):
        """
        Compute the median clip correction on one image.

        Parameters
        ----------
        radio: pycuda.gpuarray
            A radio image
        output: pycuda.gpuarray, optional
            Output data.
        """
        assert radio.shape == self.shape
        return self.cuda_median_filter.medfilt2(radio, output=output)


CudaCCDCorrection = deprecated_class("CudaCCDCorrection is replaced with CudaCCDFilter", do_print=True)(CudaCCDFilter)


class CudaLog(Log):
    """
    Helper class to take -log(radios)
    """

    def __init__(self, radios_shape, clip_min=None, clip_max=None):
        """
        Initialize a Log processing.

        Parameters
        -----------
        radios_shape: tuple
            The shape of 3D radios stack.
        clip_min: float, optional
            Data smaller than this value is replaced by this value.
        clip_max: float, optional.
            Data bigger than this value is replaced by this value.
        """
        super().__init__(radios_shape, clip_min=clip_min, clip_max=clip_max)
        self._init_kernels()

    def _init_kernels(self):
        self._do_clip_min = int(self.clip_min is not None)
        self._do_clip_max = int(self.clip_max is not None)
        self.clip_min = np.float32(self.clip_min or 0)
        self.clip_max = np.float32(self.clip_max or 1)
        self._nlog_srcfile = get_cuda_srcfile("ElementOp.cu")
        nz, ny, nx = self.radios_shape
        self._nx = np.int32(nx)
        self._ny = np.int32(ny)
        self._nz = np.int32(nz)
        self._nthreadsperblock = (16, 16, 4)  # TODO tune ?
        self._nblocks = tuple([updiv(n, p) for n, p in zip([nx, ny, nz], self._nthreadsperblock)])

        self.nlog_kernel = CudaKernel(
            "nlog",
            filename=self._nlog_srcfile,
            signature="Piiiff",
            options=[
                "-DDO_CLIP_MIN=%d" % self._do_clip_min,
                "-DDO_CLIP_MAX=%d" % self._do_clip_max,
            ],
        )

    def take_logarithm(self, radios, clip_min=None, clip_max=None):
        """
        Take the negative logarithm of a radios chunk.

        Parameters
        -----------
        radios: `pycuda.gpuarray.GPUArray`
            Radios chunk
            If not provided, a new GPU array is created.
        clip_min: float, optional
            Before taking the logarithm, the values are clipped to this minimum.
        clip_max: float, optional
            Before taking the logarithm, the values are clipped to this maximum.
        """
        clip_min = clip_min or self.clip_min
        clip_max = clip_max or self.clip_max
        if radios.flags.c_contiguous:
            self.nlog_kernel(
                radios,
                self._nx,
                self._ny,
                self._nz,
                clip_min,
                clip_max,
                grid=self._nblocks,
                block=self._nthreadsperblock,
            )
        else:
            # map-like operations cannot be directly applied on 3D arrays
            # that are not C-contiguous. We have to process image per image.
            nz = np.int32(1)
            nthreadsperblock = (32, 32, 1)
            nblocks = tuple([updiv(n, p) for n, p in zip([int(self._nx), int(self._ny), int(nz)], nthreadsperblock)])
            for i in range(radios.shape[0]):
                self.nlog_kernel(
                    radios[i], self._nx, self._ny, nz, clip_min, clip_max, grid=nblocks, block=nthreadsperblock
                )
        return radios
