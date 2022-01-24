import numpy as np
import pytest
from nabu.testutils import generate_tests_scenarios
from nabu.misc.rotation import Rotation, __have__skimage__
from nabu.misc.rotation_cuda import CudaRotation, __has_pycuda__

if __have__skimage__:
    from skimage.transform import rotate
    from skimage.data import chelsea
    ny, nx = chelsea().shape[:2]
if __has_pycuda__:
    from nabu.cuda.utils import get_cuda_context
    import pycuda.gpuarray as garray

if __have__skimage__:
    scenarios = generate_tests_scenarios({
        # ~ "output_is_none": [False, True],
        "mode": ["edge"],
        "angle": [5., 10., 45., 57., 90.],
        "center": [None, ((nx-1)/2., (ny-1)/2.), ((nx-1)/2., ny-1)],
    })
else:
    scenarios = {}

@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.image = chelsea().mean(axis=-1, dtype=np.float32)
    if __has_pycuda__:
        cls.ctx = get_cuda_context()
        cls.d_image = garray.to_gpu(cls.image)


@pytest.mark.skipif(not(__have__skimage__), reason="Need scikit-image for rotation")
@pytest.mark.usefixtures('bootstrap')
class TestRotation:

    def _get_reference_rotation(self, config):
        return rotate(
            self.image,
            config["angle"],
            resize=False,
            center=config["center"],
            order=1,
            mode=config["mode"],
            clip=False, #
            preserve_range=False
        )

    def _check_result(self, res, config, tol):
        ref = self._get_reference_rotation(config)
        mae = np.max(np.abs(res - ref))
        err_msg = str(
            "Max error is too high for this configuration: %s" % str(config)
        )
        assert mae < tol, err_msg

    # parametrize on a class method will use the same class, and launch this
    # method with different scenarios.
    @pytest.mark.parametrize("config", scenarios)
    def test_rotation(self, config):
        R = Rotation(self.image.shape, config["angle"], center=config["center"], mode=config["mode"])
        res = R(self.image)
        self._check_result(res, config, 1e-6)

    @pytest.mark.parametrize("config", scenarios)
    def test_cuda_rotation(self, config):
        R = CudaRotation(
            self.image.shape,
            config["angle"], center=config["center"], mode=config["mode"],
            cuda_options={"ctx": self.ctx},
        )
        d_res = R(self.d_image)
        res = d_res.get()
        self._check_result(res, config, 0.5)
