import pytest
import numpy as np
from nabu.preproc.phase import PaganinPhaseRetrieval
from nabu.testutils import get_data
from nabu.thirdparty.tomopy_phase import retrieve_phase
from nabu.cuda.utils import __has_pycuda__, __has_cufft__
if __has_pycuda__:
    from nabu.preproc.phase_cuda import CudaPaganinPhaseRetrieval

scenarios = [
    {
        "distance": 1,
        "energy": 35,
        "delta_beta": 1e1,
        "margin": ((50, 50), (0, 0)),
    }
]

@pytest.fixture(scope='class', params=scenarios)
def bootstrap(request):
    cls = request.cls
    cls.paganin_config = request.param

    cls.data = get_data("mri_proj_astra.npz")["data"]
    cls.rtol = 1.1e-6
    cls.rtol_pag = 5e-3
    cls.paganin = PaganinPhaseRetrieval(cls.data.shape, **cls.paganin_config)


@pytest.mark.usefixtures('bootstrap')
class TestPaganin:
    """
    Test the Paganin phase retrieval.
    The reference implementation is tomopy.
    """

    def crop_to_margin(self, data):
        s0, s1 = self.paganin.shape_inner
        ((U, _), (L, _)) = self.paganin.margin
        return data[U:U+s0, L:L+s1]

    def test_paganin(self):
        data_tomopy = np.atleast_3d(np.copy(self.data)).T

        res_tomopy = retrieve_phase(
            data_tomopy,
            pixel_size=self.paganin.pixel_size_micron*1e-4,
            dist=self.paganin.distance_cm,
            energy=self.paganin.energy_kev,
            alpha=1./(4*3.141592**2*self.paganin.delta_beta),
        )
        res_tomopy = self.crop_to_margin(res_tomopy[0].T)

        res = self.paganin.apply_filter(self.data)

        errmax = np.max(np.abs(res - res_tomopy)/np.max(res_tomopy))
        assert errmax < self.rtol_pag, "Max error is too high"


    @pytest.mark.skipif(not(__has_pycuda__ and __has_cufft__), reason="Need pycuda and scikit-cuda for this test")
    def test_gpu_paganin(self):
        gpu_paganin = CudaPaganinPhaseRetrieval(
            self.data.shape,
            **self.paganin_config
        )
        ref = self.paganin.apply_filter(self.data)
        res = gpu_paganin.apply_filter(self.data)
        errmax = np.max(np.abs((res - ref)/np.max(ref)))
        assert errmax < self.rtol, "Max error is too high"
