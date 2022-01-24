from typing import Union
import numpy as np
import pycuda.gpuarray as garray
from ..preproc.flatfield import FlatFieldArrays
from ..cuda.kernel import CudaKernel
from ..utils import get_cuda_srcfile
from ..io.reader import load_images_from_dataurl_dict


class CudaFlatFieldArrays(FlatFieldArrays):
    def __init__(
        self,
        radios_shape: tuple,
        flats: dict,
        darks: dict,
        radios_indices=None,
        interpolation: str = "linear",
        distortion_correction=None,
        cuda_options: Union[dict, None] = None,
    ):
        """
        Initialize a flat-field normalization CUDA process.
        Please read the documentation of nabu.preproc.flatfield.FlatField for help
        on the parameters.
        """
        #
        if distortion_correction is not None:
            raise NotImplementedError(
                "Flats distortion correction is not implemented with the Cuda backend"
            )
        #
        super().__init__(
            radios_shape,
            flats,
            darks,
            radios_indices=radios_indices,
            interpolation=interpolation,
            distortion_correction=distortion_correction
        )
        self._set_cuda_options(cuda_options)
        self._init_cuda_kernels()
        self._precompute_flats_indices_weights()
        self._load_flats_and_darks_on_gpu()

    def _set_cuda_options(self, user_cuda_options):
        self.cuda_options = {"device_id": None, "ctx": None, "cleanup_at_exit": None}
        if user_cuda_options is None:
            user_cuda_options = {}
        self.cuda_options.update(user_cuda_options)

    def _init_cuda_kernels(self):
        # TODO
        if self.interpolation != "linear":
            raise ValueError(
                "Interpolation other than linar is not yet implemented in the cuda back-end"
            )
        self._cuda_fname = get_cuda_srcfile("flatfield.cu")
        self.cuda_kernel = CudaKernel(
            "flatfield_normalization",
            self._cuda_fname,
            signature="PPPiiiPP",
            options=[
                "-DN_FLATS=%d" % self.n_flats,
                "-DN_DARKS=%d" % self.n_darks,
            ]
        )
        self._nx = np.int32(self.shape[1])
        self._ny = np.int32(self.shape[0])

    def _precompute_flats_indices_weights(self):
        flats_idx = np.zeros((self.n_radios, 2), dtype=np.int32)
        flats_weights = np.zeros((self.n_radios, 2), dtype=np.float32)
        for i, idx in enumerate(self.radios_indices):
            prev_next = self.get_previous_next_indices(self._sorted_flat_indices, idx)
            if len(prev_next) == 1:  # current index corresponds to an acquired flat
                weights = (1, 0)
                f_idx = (self._flat2arrayidx[prev_next[0]], -1)
            else:  # interpolate
                prev_idx, next_idx = prev_next
                delta = next_idx - prev_idx
                w1 = 1 - (idx - prev_idx) / delta
                w2 = 1 - (next_idx - idx) / delta
                weights = (w1, w2)
                f_idx = (self._flat2arrayidx[prev_idx], self._flat2arrayidx[next_idx])
            flats_idx[i] = f_idx
            flats_weights[i] = weights
        self.flats_idx = flats_idx
        self.flats_weights = flats_weights

    def _load_flats_and_darks_on_gpu(self):
        # Flats
        self.d_flats = garray.zeros((self.n_flats,) + self.shape, np.float32)
        for i, flat_idx in enumerate(self._sorted_flat_indices):
            self.d_flats[i].set(np.ascontiguousarray(self.flats[flat_idx], dtype=np.float32))
        # Darks
        self.d_darks = garray.zeros((self.n_darks,) + self.shape, np.float32)
        for i, dark_idx in enumerate(self._sorted_dark_indices):
            self.d_darks[i].set(np.ascontiguousarray(self.darks[dark_idx], dtype=np.float32))
        self.d_darks_indices = garray.to_gpu(
            np.array(self._sorted_dark_indices, dtype=np.int32)
        )
        # Indices
        self.d_flats_indices = garray.to_gpu(self.flats_idx)
        self.d_flats_weights = garray.to_gpu(self.flats_weights)

    def normalize_radios(self, radios):
        """
        Apply a flat-field correction, with the current parameters, to a stack
        of radios.

        Parameters
        -----------
        radios_shape: `pycuda.gpuarray.GPUArray`
            Radios chunk.
        """
        if not(isinstance(radios, garray.GPUArray)):
            raise ValueError("Expected a pycuda.gpuarray (got %s)" % str(type(radios)))
        if radios.dtype != np.float32:
            raise ValueError("radios must be in float32 dtype (got %s)" % str(radios.dtype))
        if radios.shape != self.radios_shape:
            raise ValueError("Expected radios shape = %s but got %s" % (str(self.radios_shape), str(radios.shape)))
        self.cuda_kernel(
            radios,
            self.d_flats,
            self.d_darks,
            self._nx,
            self._ny,
            np.int32(self.n_radios),
            self.d_flats_indices,
            self.d_flats_weights,
        )
        return radios

CudaFlatField = CudaFlatFieldArrays

class CudaFlatFieldDataUrls(CudaFlatField):
    def __init__(
        self,
        radios_shape: tuple,
        flats: dict,
        darks: dict,
        radios_indices=None,
        interpolation: str = "linear",
        distortion_correction=None,
        cuda_options: Union[dict, None] = None,
        **chunk_reader_kwargs
    ):

        flats_arrays_dict = load_images_from_dataurl_dict(flats, **chunk_reader_kwargs)
        darks_arrays_dict = load_images_from_dataurl_dict(darks, **chunk_reader_kwargs)
        super().__init__(
            radios_shape,
            flats_arrays_dict,
            darks_arrays_dict,
            radios_indices=radios_indices,
            interpolation=interpolation,
            distortion_correction=distortion_correction,
            cuda_options=cuda_options
        )
