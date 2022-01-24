import numpy as np
import pycuda.gpuarray as garray
from ..utils import get_cuda_srcfile
from ..cuda.processing import CudaProcessing
from ..cuda.kernel import CudaKernel
from .rings import MunchDeringer
try:
    from pycudwt import Wavelets
    __have_pycudwt__ = True
except ImportError:
    __have_pycudwt__ = False
try:
    from skcuda.fft import Plan
    from skcuda.fft import fft as cufft
    from skcuda.fft import ifft as cuifft
    __have_skcuda__ = True
except ImportError:
    __have_skcuda__ = False


class CudaMunchDeringer(MunchDeringer):

    def __init__(self, sigma, sinos_shape=None, radios_shape=None, levels=None, wname='db15', cuda_options=None):
        """
        Initialize a "Munch Et Al" sinogram deringer with the Cuda backend.
        See References for more information.

        Parameters
        -----------
        sigma: float
            Standard deviation of the damping parameter. The higher value of sigma,
            the more important the filtering effect on the rings.
        levels: int, optional
            Number of wavelets decomposition levels.
            By default (None), the maximum number of decomposition levels is used.
        wname: str, optional
            Default is "db15" (Daubechies, 15 vanishing moments)
        sinos_shape: tuple, optional
            Shape of the sinogram (or sinograms stack).
            This class requires either sinos_shape or radios_shape.
        radios_shape: tuple, optional
            Shape of the projection (or projections stack)
            This class requires either sinos_shape or radios_shape.

        References
        ----------
        B. Munch, P. Trtik, F. Marone, M. Stampanoni, Stripe and ring artifact removal with
        combined wavelet-Fourier filtering, Optics Express 17(10):8567-8591, 2009.
        """
        super().__init__(
            sigma, levels=levels, wname=wname, sinos_shape=sinos_shape, radios_shape=radios_shape
        )
        self._check_can_use_wavelets()
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        self._init_pycudwt()
        self._init_fft()
        self._setup_fw_kernel()

    def _check_can_use_wavelets(self):
        if not(__have_pycudwt__ and __have_skcuda__):
            raise ValueError("Needs pycudwt and scikit-cuda to use this class")


    def _init_fft(self):
        self._fft_plans = {}
        for level, d_vcoeff in self._d_vertical_coeffs.items():
            n_angles, dwidth = d_vcoeff.shape
            # Batched vertical 1D FFT - need advanced data layout
            # http://docs.nvidia.com/cuda/cufft/#advanced-data-layout
            p_f = Plan(
                (n_angles,),
                np.float32, np.complex64,
                batch=dwidth,
                inembed=np.int32([0]),
                istride=dwidth,
                idist=1,
                onembed=np.int32([0]),
                ostride=dwidth,
                odist=1
            )
            p_i = Plan(
                (n_angles,),
                np.complex64, np.float32,
                batch=dwidth,
                inembed=np.int32([0]),
                istride=dwidth,
                idist=1,
                onembed=np.int32([0]),
                ostride=dwidth,
                odist=1
            )
            self._fft_plans[level] = {"forward": p_f, "inverse": p_i}

    def _init_pycudwt(self):
        if self.levels is None:
            self.levels = 100 # will be clipped by pycudwt
        self.sino_shape = self.sinos_shape[1:]
        self.cudwt = Wavelets(np.zeros(self.sino_shape, "f"), self.wname, self.levels)
        self.levels = self.cudwt.levels
        # Access memory allocated by "pypwt" from pycuda
        self._d_sino = garray.empty(self.sino_shape, np.float32, gpudata=self.cudwt.image_int_ptr())
        self._get_vertical_coeffs()

    def _get_vertical_coeffs(self):
        self._d_vertical_coeffs = {}
        self._d_sino_f = {}
        # Transfer the (0-memset) coefficients in order to get all the shapes
        coeffs = self.cudwt.coeffs
        for i in range(self.cudwt.levels):
            shape = coeffs[i+1][1].shape
            self._d_vertical_coeffs[i+1] = garray.empty(
                shape,
                np.float32,
                gpudata=self.cudwt.coeff_int_ptr(3*i+2)
            )
            self._d_sino_f[i+1] = garray.zeros(
                (shape[0]//2+1, shape[1]),
                dtype=np.complex64
            )


    def _setup_fw_kernel(self):
        self._fw_kernel = CudaKernel(
            "kern_fourierwavelets",
            filename=get_cuda_srcfile("fourier_wavelets.cu"),
            signature="Piif",
        )


    def _destripe_2D(self, d_sino, output):
        # set the "image" for DWT (memcpy D2D)
        self._d_sino.set(d_sino)
        # perform forward DWT
        self.cudwt.forward()
        for i in range(self.cudwt.levels):
            level = i + 1
            d_coeffs = self._d_vertical_coeffs[level]
            d_sino_f = self._d_sino_f[level]
            Ny, Nx = d_coeffs.shape
            # Batched FFT along axis 0
            cufft(
                d_coeffs,
                d_sino_f,
                self._fft_plans[level]["forward"]
            )
            # Dampen the wavelets coefficients
            self._fw_kernel(d_sino_f, Nx, Ny, self.sigma)
            # IFFT
            cuifft(
                d_sino_f,
                d_coeffs,
                self._fft_plans[level]["inverse"]
            )
        # Finally, inverse DWT
        self.cudwt.inverse()
        output.set(self._d_sino)
        return output

