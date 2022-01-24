import numpy as np
from math import sqrt, pi
from ..utils import updiv, get_cuda_srcfile, _sizeof, check_supported
from .phase import PaganinPhaseRetrieval
import pycuda.driver as cuda
from pycuda import gpuarray as garray
from ..cuda.processing import CudaProcessing
from ..cuda.kernel import CudaKernel


class CudaPaganinPhaseRetrieval(PaganinPhaseRetrieval):

    supported_paddings = ["zeros", "constant", "edge"]

    def __init__(
        self,
        shape,
        distance=0.5,
        energy=20,
        delta_beta=250.,
        pixel_size=1e-6,
        padding="edge",
        margin=None,
        cuda_options=None,
        fftw_num_threads=None,
    ):
        """
        Please refer to the documentation of
        nabu.preproc.phase.PaganinPhaseRetrieval
        """
        padding = self._check_padding(padding)
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        super().__init__(
            shape,
            distance=distance,
            energy=energy,
            delta_beta=delta_beta,
            pixel_size=pixel_size,
            padding=padding,
            margin=margin,
            use_R2C=True,
            fftw_num_threads=None,
        )
        self._init_gpu_arrays()
        self._init_fft()
        self._init_padding_kernel()
        self._init_mult_kernel()


    def _check_padding(self, padding):
        check_supported(padding, self.supported_paddings, "padding")
        if padding == "zeros":
            padding = "constant"
        return padding


    def _init_gpu_arrays(self):
        self.d_paganin_filter = garray.to_gpu(
            np.ascontiguousarray(self.paganin_filter, dtype=np.float32)
        )


    def _init_fft(self):
        # Import has to be done here, otherwise scikit-cuda creates a cuda/cublas context at import
        from silx.math.fft.cufft import CUFFT
        #
        self.cufft = CUFFT(template=self.data_padded.astype("f"))
        self.d_radio_padded = self.cufft.data_in
        self.d_radio_f = self.cufft.data_out


    def _init_padding_kernel(self):
        kern_signature = {
            "constant": "Piiiiiiiiffff",
            "edge": "Piiiiiiii"
        }
        self.padding_kernel = CudaKernel(
            "padding_%s" % self.padding,
            filename=get_cuda_srcfile("padding.cu"),
            signature=kern_signature[self.padding],
        )
        Ny, Nx = self.shape
        Nyp, Nxp = self.shape_padded
        self.padding_kernel_args = [
            self.d_radio_padded,
            Nx, Ny,
            Nxp, Nyp,
            self.pad_left_len, self.pad_right_len,
            self.pad_top_len, self.pad_bottom_len,
        ]
        # TODO configurable constant values
        if self.padding == "constant":
            self.padding_kernel_args.extend([
                0, 0, 0, 0
            ])


    def _init_mult_kernel(self):
        self.cpxmult_kernel = CudaKernel(
            "inplace_complexreal_mul_2Dby2D",
            filename=get_cuda_srcfile("ElementOp.cu"),
            signature="PPii",
        )
        self.cpxmult_kernel_args = [
            self.d_radio_f,
            self.d_paganin_filter,
            self.shape_padded[1]//2+1,
            self.shape_padded[0]
        ]


    def set_input(self, data):
        assert data.shape == self.shape
        assert data.dtype == np.float32
        # Rectangular memcopy
        # TODO profile, and if needed include this copy in the padding kernel
        if isinstance(data, np.ndarray) or isinstance(data, garray.GPUArray):
            self.d_radio_padded[:self.shape[0], :self.shape[1]] = data[:, :]
        elif isinstance(data, cuda.DeviceAllocation):
            # TODO manual memcpy2D
            raise NotImplementedError("pycuda buffers are not supported yet")
        else:
            raise ValueError("Expected either numpy array, pycuda array or pycuda buffer")


    def get_output(self, output):
        s0, s1 = self.shape_inner
        ((U, _), (L, _)) = self.margin
        if output is None:
            # copy D2H
            return  self.d_radio_padded[U:U + s0, L:L + s1].get()
        assert output.shape == self.shape_inner
        assert output.dtype == np.float32
        output[:, :] = self.d_radio_padded[U:U + s0, L:L + s1]
        return output


    def apply_filter(self, radio, output=None):
        self.set_input(radio)

        self.padding_kernel(*self.padding_kernel_args)
        self.cufft.fft(self.d_radio_padded, output=self.d_radio_f)
        self.cpxmult_kernel(*self.cpxmult_kernel_args)
        self.cufft.ifft(self.d_radio_f, output=self.d_radio_padded)

        return self.get_output(output)


    __call__ = apply_filter
