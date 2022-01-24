import os
import numpy as np
import pytest
import h5py
from nabu.testutils import utilstest, __do_long_tests__
from nabu.estimation.focus import CameraFocus

@pytest.fixture(scope="class")
def bootstrap_fcs(request):
    cls = request.cls
    cls.abs_tol_dist = 1e-2
    cls.abs_tol_tilt = 2.5e-4

    (
        cls.data,
        cls.img_pos,
        cls.pixel_size,
        (calib_data_std, calib_data_angle),
    ) = get_focus_data("test_alignment_focus.h5")
    (
        cls.angle_best_ind,
        cls.angle_best_pos,
        cls.angle_tilt_v,
        cls.angle_tilt_h,
    ) = calib_data_angle
    cls.std_best_ind, cls.std_best_pos = calib_data_std


def get_focus_data(*dataset_path):
    """
    Get a dataset file from silx.org/pub/nabu/data
    dataset_args is a list describing a nested folder structures, ex.
    ["path", "to", "my", "dataset.h5"]
    """
    dataset_relpath = os.path.join(*dataset_path)
    dataset_downloaded_path = utilstest.getfile(dataset_relpath)
    with h5py.File(dataset_downloaded_path, "r") as hf:
        data = hf["/entry/instrument/detector/data"][()]
        img_pos = hf["/entry/instrument/detector/distance"][()]

        pixel_size = np.mean(
            [
                hf["/entry/instrument/detector/x_pixel_size"][()],
                hf["/entry/instrument/detector/y_pixel_size"][()],
            ]
        )

        angle_best_ind = hf["/calibration/focus/angle/best_img"][()]
        angle_best_pos = hf["/calibration/focus/angle/best_pos"][()]
        angle_tilt_v = hf["/calibration/focus/angle/tilt_v_rad"][()]
        angle_tilt_h = hf["/calibration/focus/angle/tilt_h_rad"][()]

        std_best_ind = hf["/calibration/focus/std/best_img"][()]
        std_best_pos = hf["/calibration/focus/std/best_pos"][()]

    calib_data_angle = (angle_best_ind, angle_best_pos, angle_tilt_v, angle_tilt_h)
    calib_data_std = (std_best_ind, std_best_pos)
    return data, img_pos, pixel_size, (calib_data_std, calib_data_angle)




@pytest.mark.skipif(not (__do_long_tests__), reason="need environment variable NABU_LONG_TESTS=1")
@pytest.mark.usefixtures("bootstrap_fcs")
class TestFocus:
    def test_find_distance(self):
        focus_calc = CameraFocus()
        focus_pos, focus_ind = focus_calc.find_distance(self.data, self.img_pos)

        message = "Computed focus motor position %f " % focus_pos + " and expected %f do not coincide" % self.std_best_pos
        assert np.isclose(self.std_best_pos, focus_pos, atol=self.abs_tol_dist), message

        message = "Computed focus image index %f " % focus_ind + " and expected %f do not coincide" % self.std_best_ind
        assert np.isclose(self.std_best_ind, focus_ind, atol=self.abs_tol_dist), message

    def test_find_scintillator_tilt(self):
        focus_calc = CameraFocus()
        focus_pos, focus_ind, tilts_vh = focus_calc.find_scintillator_tilt(self.data, self.img_pos)

        message = "Computed focus motor position %f " % focus_pos + " and expected %f do not coincide" % self.angle_best_pos
        assert np.isclose(self.angle_best_pos, focus_pos, atol=self.abs_tol_dist), message

        message = "Computed focus image index %f " % focus_ind + " and expected %f do not coincide" % self.angle_best_ind
        assert np.isclose(self.angle_best_ind, focus_ind, atol=self.abs_tol_dist), message

        expected_tilts_vh = np.squeeze(np.array([self.angle_tilt_v, self.angle_tilt_h]))
        computed_tilts_vh = -tilts_vh / (self.pixel_size / 1000)
        message = "Computed tilts %s and expected %s do not coincide" % (
            computed_tilts_vh,
            expected_tilts_vh,
        )
        assert np.all(np.isclose(computed_tilts_vh, expected_tilts_vh, atol=self.abs_tol_tilt)), message

    def test_size_determination(self):
        inp_shape = [2162, 2560]
        exp_shape = np.array([2160, 2160])
        new_shape = CameraFocus()._check_img_block_size(inp_shape, 4, suggest_new_shape=True)

        message = "New suggested shape: %s and expected: %s do not coincide" % (new_shape, exp_shape)
        assert np.all(new_shape == exp_shape), message
