import numpy as np
from math import floor
from .shift import VerticalShift
from ..cuda.utils import __has_pycuda__
if __has_pycuda__:
    import pycuda.gpuarray as garray


class CudaVerticalShift(VerticalShift):
    def __init__(self, radios_shape, shifts):
        """
        Vertical Shifter, Cuda backend.
        """
        super().__init__(radios_shape, shifts)
        self._init_cuda_arrays()


    def _init_cuda_arrays(self):
        interp_infos_arr = np.zeros((len(self.interp_infos), 2), "f")
        self._d_interp_infos = garray.to_gpu(interp_infos_arr)
        self._d_radio_tmp = garray.zeros(self.radios_shape[1:], "f")


    def apply_vertical_shifts(self, radios, iangles, output=None):
        """
        Parameters
        ----------
        radios: 3D pycuda.gpuarray.GPUArray
            The input radios. If the optional parameter is not given, they are modified in-place
        iangles:  a sequence of integers
            Must have the same lenght as radios.
            It contains the index at which the shift is found in `self.shifts`
            given by `shifts` argument in the initialisation of the object.
        output: 3D pycuda.gpuarray.GPUArray, optional
            If given, it will be modified to contain the shifted radios.
            Must be of the same shape of `radios`.
        """
        self._check(radios, iangles)
        n_z = self.radios_shape[1]

        for ia in iangles:
            radio = radios[ia]
            self._d_radio_tmp.fill(0)
            S0, f = self.interp_infos[ia]
            s0 = S0

            if s0 > 0:
                self._d_radio_tmp[:-s0] = radio[s0:]
                self._d_radio_tmp[:-s0] *= (1 - f)

            elif s0 == 0:
                self._d_radio_tmp[:] = radio[s0:]
                self._d_radio_tmp[:] *= (1 - f)
            else:
                self._d_radio_tmp[-s0:] = radio[:s0]
                self._d_radio_tmp[-s0:] *= (1 - f)

            s0 = S0 + 1
            f = np.float32(f)

            #  "radios[] * f"  is out of place but 2D
            if s0 > 0:
                if s0 < n_z:
                    self._d_radio_tmp[:-s0] += radio[s0:] * f
            elif s0 == 0:
                self._d_radio_tmp[:] += radio[s0:] * f
            else:
                self._d_radio_tmp[-s0:] += radio[:s0] * f

            if output is None:
                radios[ia, :, :] = self._d_radio_tmp[:]
            else:
                output[ia, :, :] = self._d_radio_tmp[:]
