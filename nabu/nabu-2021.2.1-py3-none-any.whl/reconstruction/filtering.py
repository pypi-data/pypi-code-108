from math import pi
import pycuda.gpuarray as garray
import numpy as np
from silx.image.tomography import compute_fourier_filter, get_next_power
from ..cuda.kernel import CudaKernel
from ..cuda.processing import CudaProcessing
from ..utils import get_cuda_srcfile, check_supported, updiv

class SinoFilter:

    available_padding_modes = ["zeros", "edges"]

    def __init__(
        self,
        sino_shape,
        filter_name=None,
        padding_mode="zeros",
        extra_options=None,
        cuda_options=None,
    ):
        """
        Build a sinogram filter process.
        """
        self.cuda = CudaProcessing(**(cuda_options or {}))
        self._init_extra_options(extra_options)
        self._calculate_shapes(sino_shape)
        self._init_fft()
        self._allocate_memory(sino_shape)
        self._compute_filter(filter_name)
        self._set_padding_mode(padding_mode)
        self._init_kernels()


    def _init_extra_options(self, extra_options):
        self.extra_options = {
            "cutoff": 1.,
        }
        if extra_options is not None:
            self.extra_options.update(extra_options)

    def _set_padding_mode(self, padding_mode):
        # Compat.
        if padding_mode == "edge":
            padding_mode = "edges"
        #
        check_supported(padding_mode, self.available_padding_modes, "padding mode")
        self.padding_mode = padding_mode


    def _calculate_shapes(self, sino_shape):
        self.ndim = len(sino_shape)
        if self.ndim == 2:
            n_angles, dwidth = sino_shape
            n_sinos = 1
        elif self.ndim == 3:
            n_sinos, n_angles, dwidth = sino_shape
        else:
            raise ValueError("Invalid sinogram number of dimensions")
        self.sino_shape = sino_shape
        self.n_angles = n_angles
        self.dwidth = dwidth
        # int() is crucial here ! Otherwise some pycuda arguments (ex. memcpy2D)
        # will not work with numpy.int64 (as for 2018.X)
        self.dwidth_padded = int(get_next_power(2*self.dwidth))
        self.sino_padded_shape = (n_angles, self.dwidth_padded)
        if self.ndim == 3:
            self.sino_padded_shape = (n_sinos, ) + self.sino_padded_shape
        sino_f_shape = list(self.sino_padded_shape)
        sino_f_shape[-1] = sino_f_shape[-1]//2+1
        self.sino_f_shape = tuple(sino_f_shape)
        #
        self.pad_left = (self.dwidth_padded - self.dwidth)//2
        self.pad_right = self.dwidth_padded - self.dwidth - self.pad_left


    def _init_fft(self):
        # Import has to be done here, otherwise scikit-cuda creates a cuda/cublas context at import
        from silx.math.fft.cufft import CUFFT
        #
        self.fft = CUFFT(
            self.sino_padded_shape,
            dtype=np.float32,
            axes=(-1,),
        )


    def _allocate_memory(self, sino_shape):
        self.d_filter_f = garray.zeros((self.sino_f_shape[-1],), np.complex64)
        self.d_sino_padded = self.fft.data_in
        self.d_sino_f = self.fft.data_out


    def set_filter(self, h_filt, normalize=True):
        """
        Set a filter for sinogram filtering.

        :param h_filt: Filter. Each line of the sinogram will be filtered with
            this filter. It has to be the Real-to-Complex Fourier Transform
            of some real filter, padded to 2*sinogram_width.
        :param normalize: Whether to normalize the filter with pi/num_angles.
        """
        if h_filt.size != self.sino_f_shape[-1]:
            raise ValueError(
                """
                Invalid filter size: expected %d, got %d.
                Please check that the filter is the Fourier R2C transform of
                some real 1D filter.
                """
                % (self.sino_f_shape[-1], h_filt.size)
            )
        if not(np.iscomplexobj(h_filt)):
            print("Warning: expected a complex Fourier filter")
        self.filter_f = h_filt
        if normalize:
            self.filter_f *= pi/self.n_angles
        self.filter_f = self.filter_f.astype(np.complex64)
        self.d_filter_f[:] = self.filter_f[:]


    def _compute_filter(self, filter_name):
        self.filter_name = filter_name or "ram-lak"
        filter_f = compute_fourier_filter(
            self.dwidth_padded,
            self.filter_name,
            cutoff=self.extra_options["cutoff"],
        )[:self.dwidth_padded//2+1]  # R2C
        self.set_filter(filter_f, normalize=True)


    def _init_kernels(self):
        fname = get_cuda_srcfile("ElementOp.cu")
        if self.ndim == 2:
            kernel_name = "inplace_complex_mul_2Dby1D"
            kernel_sig = "PPii"
        else:
            kernel_name = "inplace_complex_mul_3Dby1D"
            kernel_sig = "PPiii"
        self.mult_kernel = CudaKernel(
            kernel_name,
            filename=fname,
            signature=kernel_sig
        )
        self.kern_args = (self.d_sino_f, self.d_filter_f)
        self.kern_args += (self.d_sino_f.shape[::-1])
        self._pad_edges_kernel = CudaKernel(
            "padding_edge",
            filename=get_cuda_srcfile("padding.cu"),
            signature="Piiiiiiii"
        )
        self._pad_block = (32, 32, 1)
        self._pad_grid = tuple([updiv(n, p) for n, p in zip(self.sino_padded_shape[::-1], self._pad_block)])


    def _check_array(self, arr):
        if arr.dtype != np.float32:
            raise ValueError("Expected data type = numpy.float32")
        if arr.shape != self.sino_shape:
            raise ValueError("Expected sinogram shape %s, got %s" % (self.sino_shape, arr.shape))


    def _pad_sino(self, sino):
        if self.padding_mode == "edges":
            self.d_sino_padded[:, :self.dwidth] = sino[:]
            self._pad_edges_kernel(
                self.d_sino_padded,
                self.dwidth,
                self.n_angles,
                self.dwidth_padded,
                self.n_angles,
                self.pad_left,
                self.pad_right,
                0,
                0,
                grid=self._pad_grid,
                block=self._pad_block
            )
        else: # zeros
            self.d_sino_padded.fill(0)
            if self.ndim == 2:
                self.d_sino_padded[:, :self.dwidth] = sino[:]
            else:
                self.d_sino_padded[:, :, :self.dwidth] = sino[:]


    def filter_sino(self, sino, output=None, no_output=False):
        """
        Perform the sinogram siltering.

        Parameters
        ----------
        sino: numpy.ndarray or pycuda.gpuarray.GPUArray
            Input sinogram (2D or 3D)
        output: numpy.ndarray or pycuda.gpuarray.GPUArray, optional
            Output array.
        no_output: bool, optional
            If set to True, no copy is be done. The resulting data lies
            in self.d_sino_padded.
        """
        self._check_array(sino)
        # copy2d/copy3d
        self._pad_sino(sino)
        # FFT
        self.fft.fft(self.d_sino_padded, output=self.d_sino_f)

        # multiply padded sinogram with filter in the Fourier domain
        self.mult_kernel(*self.kern_args) # TODO tune block size ?

        # iFFT
        self.fft.ifft(self.d_sino_f, output=self.d_sino_padded)

        # return
        if no_output:
            return self.d_sino_padded
        if output is None:
            res = np.zeros(self.sino_shape, dtype=np.float32)
            # can't do memcpy2d D->H ? (self.d_sino_padded[:, w]) I have to get()
            sino_ref = self.d_sino_padded.get()
        else:
            res = output
            sino_ref = self.d_sino_padded
        if self.ndim == 2:
            res[:] = sino_ref[:, :self.dwidth]
        else:
            res[:] = sino_ref[:, :, :self.dwidth]
        return res

    __call__ = filter_sino
