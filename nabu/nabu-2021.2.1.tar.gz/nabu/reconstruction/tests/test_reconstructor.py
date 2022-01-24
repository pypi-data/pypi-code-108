import numpy as np
import pytest
from nabu.testutils import get_big_data, __big_testdata_dir__, compare_arrays, generate_tests_scenarios, __do_long_tests__
from nabu.cuda.utils import __has_pycuda__, __has_cufft__, get_cuda_context
__has_cuda_fbp__ = (__has_cufft__ and __has_pycuda__)
if __has_cuda_fbp__:
    from nabu.reconstruction.reconstructor_cuda import CudaReconstructor
    from nabu.reconstruction.fbp import Backprojector as CudaBackprojector
    import pycuda.gpuarray as garray





scenarios = generate_tests_scenarios({
    "axis": ["z", "y", "x"],
    "vol_type": ["sinograms", "projections"],
    "indices": [(300, 310)], # reconstruct 10 slices
    "slices_roi": [
        None,
        (None, None, 200, 400),
        (250, 300, None, None),
        (120, 330, 301, 512)
    ],
})


@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.projs = get_big_data("MRI512_projs.npy")
    if __has_cuda_fbp__:
        cls.ctx = get_cuda_context()
        cls.d_projs = garray.to_gpu(cls.projs)
    cls.ref = None
    cls.tol = 5e-2


@pytest.mark.skipif(
    __big_testdata_dir__ is None or not(__do_long_tests__),
    reason="need environment variable NABU_BIGDATA_DIR and NABU_LONG_TESTS=1"
)
@pytest.mark.usefixtures('bootstrap')
class TestReconstructor:

    @pytest.mark.skipif(not(__has_cuda_fbp__), reason="need pycuda and scikit-cuda")
    @pytest.mark.parametrize("config", scenarios)
    def test_cuda_reconstructor(self, config):
        data = self.projs
        d_data = self.d_projs
        if config["vol_type"] == "sinograms":
            data = np.moveaxis(self.projs, 1, 0)
            d_data = self.d_projs.transpose(axes=(1, 0, 2)) # view
        reconstructor = CudaReconstructor(
            data.shape,
            config["indices"],
            axis=config["axis"],
            vol_type=config["vol_type"],
            slices_roi=config["slices_roi"]
        )
        res = reconstructor.reconstruct(d_data)
        ref = self.get_ref()
        ref = self.crop_array(ref, config)
        err_max = np.max(np.abs(res - ref))
        assert err_max < self.tol, "something wrong with reconstructor, config = %s" % str(config)


    def get_ref(self):
        if self.ref is not None:
            return self.ref
        if __has_cuda_fbp__:
            fbp_cls = CudaBackprojector
        ref = np.zeros((512, 512, 512), "f")
        fbp = fbp_cls((self.projs.shape[0], self.projs.shape[-1]))
        for i in range(512):
            ref[i] = fbp.fbp(self.d_projs[:, i, :])
        self.ref = ref
        return self.ref


    @staticmethod
    def crop_array(arr, config):
        indices = config["indices"]
        axis = config["axis"]
        slices_roi = config["slices_roi"] or (None, None, None, None)
        i_slice = slice(*indices)
        u_slice = slice(*slices_roi[:2])
        v_slice = slice(*slices_roi[-2:])
        if axis == "z":
            z_slice, y_slice, x_slice = i_slice, v_slice, u_slice
        if axis == "y":
            z_slice, y_slice, x_slice = v_slice, i_slice, u_slice
        if axis == "x":
            z_slice, y_slice, x_slice = v_slice, u_slice, i_slice
        return arr[z_slice, y_slice, x_slice]


