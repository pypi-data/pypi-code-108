import numpy as np
from pycuda import gpuarray as garray
from ..utils import calc_padding_lengths, updiv, get_cuda_srcfile
from ..cuda.processing import CudaProcessing
from ..cuda.kernel import CudaKernel
from ..cuda.padding import CudaPadding
from .phase_cuda import CudaPaganinPhaseRetrieval
from .ctf import CTFPhaseRetrieval


# TODO:
#  - better padding scheme (for now 2*shape)
#  - rework inheritance scheme ? (base class SingleDistancePhaseRetrieval and its cuda counterpart)
class CudaCTFPhaseRetrieval(CTFPhaseRetrieval):

    """
    Cuda back-end of CTFPhaseRetrieval
    """

    def __init__(
        self, shape, geo_pars, delta_beta,
        padding_mode="reflect", lim1=1.0e-5, lim2=0.2, use_rfft=True,
        logger=None, cuda_options=None,
    ):
        """
        Initialize a CudaCTFPhaseRetrieval.

        Parameters
        ----------
        shape: tuple
            Shape of the images to process
        padding_mode: str
            Padding mode. Default is "reflect".

        Other parameters
        -----------------
        Please refer to CTFPhaseRetrieval documentation.
        """
        if not use_rfft:
            raise ValueError("Only use_rfft=True is supported")
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        super().__init__(geo_pars, delta_beta, lim1=lim1, lim2=lim2, logger=logger, use_rfft=True)
        self._calc_shape(shape)
        self._init_ctf_filter()
        self._init_padding(padding_mode)
        self._init_fft()
        self._init_mult_kernel()


    def _calc_shape(self, shape):
        if np.isscalar(shape):
            shape = (shape, shape)
        else:
            assert len(shape) == 2
        self.shape = shape
        n_y0, n_x0 = self.shape
        n_y_p = 2 * n_y0
        n_x_p = 2 * n_x0
        self.shape_padded = (n_y_p, n_x_p)


    def _init_ctf_filter(self):
        self.require_filter_for_shape(self.shape_padded)
        self._mean_scale_factor = self.unreg_filter_denom[0, 0] * np.prod(self.shape_padded)
        self._d_filter_num = garray.to_gpu(self.unreg_filter_denom).astype("f")
        self._d_filter_denom = garray.to_gpu(
            (1. / (2 * self.unreg_filter_denom * self.unreg_filter_denom + self.lim)).astype("f")
        )


    def _init_padding(self, padding_mode):
        self.padding_mode = padding_mode
        pad_width = calc_padding_lengths(self.shape, self.shape_padded)
        # Custom coordinate transform to get directly FFT layout
        R, C = np.indices(self.shape, dtype=np.int32)
        coords_R = np.roll(
            np.pad(R, pad_width, mode=padding_mode),
            (-pad_width[0][0], -pad_width[1][0]),
            axis=(0, 1)
        )
        coords_C = np.roll(
            np.pad(C, pad_width, mode=padding_mode),
            (-pad_width[0][0], -pad_width[1][0]),
            axis=(0, 1)
        )
        self.cuda_padding = CudaPadding(
            self.shape,
            (coords_R, coords_C),
            mode=self.padding_mode,
            # propagate cuda options ?
        )


    def _init_fft(self):
        # Import has to be done here, otherwise scikit-cuda creates a cuda/cublas context at import
        from silx.math.fft.cufft import CUFFT
        self.cufft = CUFFT(template=np.zeros(self.shape_padded, dtype="f"))
        self.d_radio_padded = self.cufft.data_in
        self.d_radio_f = self.cufft.data_out


    def _init_mult_kernel(self):
        self.cpxmult_kernel = CudaKernel(
            "CTF_kernel",
            filename=get_cuda_srcfile("ElementOp.cu"),
            signature="PPPfii",
        )
        Nx = np.int32(self.shape_padded[1]//2 + 1)
        Ny = np.int32(self.shape_padded[0])
        self._cpxmult_kernel_args = [
            self.d_radio_f,
            self._d_filter_num,
            self._d_filter_denom,
            np.float32(self._mean_scale_factor),
            Nx,
            Ny
        ]
        blk = (32, 32, 1)
        grd = (updiv(Nx, blk[0]), updiv(Ny, blk[1]))
        self._cpxmult_kernel_kwargs = {"grid": grd, "block": blk}


    set_input = CudaPaganinPhaseRetrieval.set_input


    def retrieve_phase(self, image, output=None, normalize_by_mean=False):
        """
        Perform padding on an image. Please see the documentation of CTFPhaseRetrieval.retrieve_phase().
        """
        self.set_input(image)
        self.cuda_padding.pad(image, output=self.d_radio_padded)
        if normalize_by_mean:
            m = garray.sum(self.d_radio_padded).get() / np.prod(self.shape_padded)
            self.d_radio_padded /= m
        self.cufft.fft(self.d_radio_padded, output=self.d_radio_f)
        self.cpxmult_kernel(*self._cpxmult_kernel_args, **self._cpxmult_kernel_kwargs)
        self.cufft.ifft(self.d_radio_f, output=self.d_radio_padded)

        if output is None:
            output = self.cuda_processing.allocate_array("d_output", self.shape)
        output[:, :] = self.d_radio_padded[:self.shape[0], :self.shape[1]]
        return output
