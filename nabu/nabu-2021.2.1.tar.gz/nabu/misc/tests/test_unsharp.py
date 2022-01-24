import numpy as np
import pytest
from scipy.misc import ascent
from nabu.misc.unsharp import UnsharpMask
from nabu.misc.unsharp_opencl import OpenclUnsharpMask, __have_opencl__
from nabu.cuda.utils import __has_pycuda__
if __have_opencl__:
    import pyopencl.array as parray
if __has_pycuda__:
    import pycuda.gpuarray as garray
    from nabu.misc.unsharp_cuda import CudaUnsharpMask

@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.data = np.ascontiguousarray(ascent()[:, :511], dtype=np.float32)
    cls.tol = 1e-4
    cls.sigma = 1.6
    cls.coeff = 0.5
    cls.compute_reference()


@pytest.mark.usefixtures('bootstrap')
class TestUnsharp:

    @classmethod
    def compute_reference(cls):
        cls.Unsharp = UnsharpMask(cls.data.shape, cls.sigma, cls.coeff)
        cls.ref = cls.Unsharp.unsharp(cls.data)

    @pytest.mark.skipif(not(__have_opencl__), reason="Need pyopencl for this test")
    def testOpenclUnsharp(self):
        ClUnsharp = OpenclUnsharpMask(self.data.shape, self.sigma, self.coeff)
        d_image = parray.to_device(ClUnsharp.queue, self.data)
        d_out = parray.zeros_like(d_image)
        ClUnsharp.unsharp(d_image, d_out)
        mae = np.max(np.abs(d_out.get() - self.ref))
        assert mae < self.tol, "Max error is too high (%.2e > %.2e)" % (mae, self.tol)

    @pytest.mark.skipif(not(__has_pycuda__), reason="Need cuda/pycuda for this test")
    def testCudaUnsharp(self):
        CuUnsharp = CudaUnsharpMask(self.data.shape, self.sigma, self.coeff)
        d_image = garray.to_gpu(self.data)
        d_out = garray.zeros_like(d_image)
        CuUnsharp.unsharp(d_image, d_out)
        mae = np.max(np.abs(d_out.get() - self.ref))
        assert mae < self.tol, "Max error is too high (%.2e > %.2e)" % (mae, self.tol)
