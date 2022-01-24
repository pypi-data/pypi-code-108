import pytest
import numpy as np
from nabu.estimation.tilt import CameraTilt
from nabu.estimation.tests.test_cor import bootstrap_cor
try:
    import skimage.transform as skt  # noqa: F401
    __have_skimage__ = True
except ImportError:
    __have_skimage__ = False


@pytest.mark.usefixtures("bootstrap_cor")
class TestCameraTilt:
    def test_1dcorrelation(self):
        radio1 = self.data[0, :, :]
        radio2 = np.fliplr(self.data[1, :, :])

        tilt_calc = CameraTilt()
        cor_position, camera_tilt = tilt_calc.compute_angle(radio1, radio2)

        message = "Computed tilt %f " % camera_tilt + " and real tilt %f do not coincide" % self.tilt_deg
        assert np.isclose(self.tilt_deg, camera_tilt, atol=self.abs_tol), message

        message = "Computed CoR %f " % cor_position + " and real CoR %f do not coincide" % self.cor_hl_pix
        assert np.isclose(self.cor_gl_pix, cor_position, atol=self.abs_tol), message

    @pytest.mark.skipif(not (__have_skimage__), reason="need scikit-image for this test")
    def test_fftpolar(self):
        radio1 = self.data[0, :, :]
        radio2 = np.fliplr(self.data[1, :, :])

        tilt_calc = CameraTilt()
        cor_position, camera_tilt = tilt_calc.compute_angle(radio1, radio2, method="fft-polar")

        message = "Computed tilt %f " % camera_tilt + " and real tilt %f do not coincide" % self.tilt_deg
        assert np.isclose(self.tilt_deg, camera_tilt, atol=self.abs_tol), message

        message = "Computed CoR %f " % cor_position + " and real CoR %f do not coincide" % self.cor_hl_pix
        assert np.isclose(self.cor_gl_pix, cor_position, atol=self.abs_tol), message
