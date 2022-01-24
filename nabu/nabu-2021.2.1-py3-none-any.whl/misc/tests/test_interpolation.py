import numpy as np
import pytest
from scipy.misc import ascent
from scipy.interpolate import interp1d
from nabu.testutils import generate_tests_scenarios
from nabu.utils import get_cuda_srcfile, updiv
from nabu.cuda.utils import __has_pycuda__, get_cuda_context
if __has_pycuda__:
    import pycuda.gpuarray as garray
    from nabu.cuda.kernel import CudaKernel


img0 = ascent().astype("f")

scenarios = generate_tests_scenarios({
    "image": [
        img0, img0[:, :511], img0[:511, :]
    ],
    "x_bounds": [
        (180, 360), (0, 180), (50, 50+180)
    ],
    "x_to_x_new": [
        0.1, -0.2, 0.3
    ],
})

@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.tol = 1e-4
    if __has_pycuda__:
        cls.ctx = get_cuda_context()


@pytest.mark.usefixtures('bootstrap')
class TestInterpolation:

    def _get_reference_interpolation(self, img, x, x_new):
        interpolator = interp1d(
            x, img, kind="linear", axis=0, fill_value="extrapolate", copy=True
        )
        ref = interpolator(x_new)
        return ref

    def _compare(self, res, img, x, x_new):
        ref = self._get_reference_interpolation(img, x, x_new)
        mae = np.max(np.abs(res - ref))
        return mae


    # parametrize on a class method will use the same class, and launch this
    # method with different scenarios.
    @pytest.mark.skipif(not(__has_pycuda__), reason="need pycuda for this test")
    @pytest.mark.parametrize("config", scenarios)
    def test_cuda_interpolation(self, config):
        img = config["image"]
        Ny, Nx = img.shape

        xmin, xmax = config["x_bounds"]
        x = np.linspace(xmin, xmax, num=img.shape[0], endpoint=False, dtype="f")
        x_new = x + config["x_to_x_new"]

        d_img = garray.to_gpu(img)
        d_out = garray.zeros_like(d_img)
        d_x = garray.to_gpu(x)
        d_x_new = garray.to_gpu(x_new)

        cuda_interpolator = CudaKernel(
            "linear_interp_vertical",
            get_cuda_srcfile("interpolation.cu"),
            signature="PPiiPP"
        )
        cuda_interpolator(
            d_img, d_out, Nx, Ny, d_x, d_x_new,
            grid=(updiv(Nx, 16), updiv(Ny, 16), 1), block=(16, 16, 1)
        )
        err = self._compare(d_out.get(), img, x, x_new)
        err_msg = str(
            "Max error is too high for this configuration: %s" % str(config)
        )
        assert err < self.tol, err_msg
