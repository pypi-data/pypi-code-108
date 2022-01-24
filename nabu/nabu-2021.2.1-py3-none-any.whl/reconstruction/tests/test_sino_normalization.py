import os.path as path
import numpy as np
import pytest
from nabu.testutils import get_data
from nabu.cuda.utils import __has_pycuda__
from nabu.preproc.sinogram import SinoNormalization
if __has_pycuda__:
    from nabu.preproc.sinogram_cuda import CudaSinoNormalization
    import pycuda.gpuarray as garray


@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls
    cls.sino = get_data("sino_refill.npy")
    cls.tol = 1e-7


@pytest.mark.usefixtures("bootstrap")
class TestSinoNormalization:

    def test_sino_normalization(self):
        sino_proc = SinoNormalization(
            kind="chebyshev", sinos_shape=self.sino.shape
        )
        sino = self.sino.copy()
        sino_proc.normalize(sino)


    @pytest.mark.skipif(not(__has_pycuda__), reason="Need pycuda for sinogram normalization with cuda backend")
    def test_dff_cuda(self):
        sino_proc = SinoNormalization(
            kind="chebyshev", sinos_shape=self.sino.shape
        )
        sino = self.sino.copy()
        ref = sino_proc.normalize(sino)

        cuda_sino_proc = CudaSinoNormalization(
            kind="chebyshev", sinos_shape=self.sino.shape
        )
        d_sino = garray.to_gpu(self.sino)
        cuda_sino_proc.normalize(d_sino)
        res = d_sino.get()

        assert np.max(np.abs(res - ref)) < self.tol

