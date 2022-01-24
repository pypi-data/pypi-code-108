import numpy as np
import pytest
from nabu.estimation.alignment import AlignmentBase

@pytest.fixture(scope="class")
def bootstrap_base(request):
    cls = request.cls
    cls.abs_tol = 2.5e-2


@pytest.mark.usefixtures("bootstrap_base")
class TestAlignmentBase:
    def test_peak_fitting_2d_3x3(self):
        # Fit a 3 x 3 grid
        fy = np.linspace(-1, 1, 3)
        fx = np.linspace(-1, 1, 3)
        yy, xx = np.meshgrid(fy, fx, indexing="ij")

        peak_pos_yx = np.random.rand(2) * 1.6 - 0.8
        f_vals = np.exp(-((yy - peak_pos_yx[0]) ** 2 + (xx - peak_pos_yx[1]) ** 2) / 100)

        fitted_peak_pos_yx = AlignmentBase.refine_max_position_2d(f_vals, fy, fx)

        message = (
            "Computed peak position: (%f, %f) " % (*fitted_peak_pos_yx,)
            + " and real peak position (%f, %f) do not coincide." % (*peak_pos_yx,)
            + " Difference: (%f, %f)," % (*(fitted_peak_pos_yx - peak_pos_yx),)
            + " tolerance: %f" % self.abs_tol
        )
        assert np.all(np.isclose(peak_pos_yx, fitted_peak_pos_yx, atol=self.abs_tol)), message

    def test_peak_fitting_2d_error_checking(self):
        # Fit a 3 x 3 grid
        fy = np.linspace(-1, 1, 3)
        fx = np.linspace(-1, 1, 3)
        yy, xx = np.meshgrid(fy, fx, indexing="ij")

        peak_pos_yx = np.random.rand(2) + 1.5
        f_vals = np.exp(-((yy - peak_pos_yx[0]) ** 2 + (xx - peak_pos_yx[1]) ** 2) / 100)

        with pytest.raises(ValueError) as ex:
            AlignmentBase.refine_max_position_2d(f_vals, fy, fx)

        message = (
            "Error should have been raised about the peak being fitted outside margins, "
            + "other error raised instead:\n%s" % str(ex.value)
        )
        assert "positions are outside the input margins" in str(ex.value), message

    def test_extract_peak_regions_1d(self):
        img = np.random.randint(0, 10, size=(8, 8))

        peaks_pos = np.argmax(img, axis=-1)
        peaks_val = np.max(img, axis=-1)

        cc_coords = np.arange(0, 8)

        (
            found_peaks_val,
            found_peaks_pos,
        ) = AlignmentBase.extract_peak_regions_1d(img, axis=-1, cc_coords=cc_coords)
        message = "The found peak positions do not correspond to the expected peak positions:\n  Expected: %s\n  Found: %s" % (
            peaks_pos,
            found_peaks_pos[1, :],
        )
        assert np.all(peaks_val == found_peaks_val[1, :]), message
