import os
import numpy as np
import pytest
import h5py
from nabu.testutils import utilstest
from nabu.estimation.translation import DetectorTranslationAlongBeam
import scipy.ndimage

def get_alignxc_data(*dataset_path):
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

        unit_length_shifts_vh = [
            hf["/calibration/alignxc/y_pixel_shift_unit"][()],
            hf["/calibration/alignxc/x_pixel_shift_unit"][()],
        ]
        all_shifts_vh = hf["/calibration/alignxc/yx_pixel_offsets"][()]

    return data, img_pos, (unit_length_shifts_vh, all_shifts_vh)

@pytest.fixture(scope="class")
def bootstrap_dtr(request):
    cls = request.cls
    cls.abs_tol = 1e-1
    cls.data, cls.img_pos, calib_data = get_alignxc_data("test_alignment_alignxc.h5")
    cls.expected_shifts_vh, cls.all_shifts_vh = calib_data


@pytest.mark.usefixtures("bootstrap_dtr")
class TestDetectorTranslation:
    def test_alignxc(self):
        T_calc = DetectorTranslationAlongBeam()

        shifts_v, shifts_h, found_shifts_list = T_calc.find_shift(self.data, self.img_pos, return_shifts=True)

        message = "Computed shifts coefficients %s and expected %s do not coincide" % (
            (shifts_v, shifts_h),
            self.expected_shifts_vh,
        )
        assert np.all(np.isclose(self.expected_shifts_vh, [shifts_v, shifts_h], atol=self.abs_tol)), message

        message = "Computed shifts %s and expected %s do not coincide" % (
            found_shifts_list,
            self.all_shifts_vh,
        )
        assert np.all(np.isclose(found_shifts_list, self.all_shifts_vh, atol=self.abs_tol)), message

    def test_alignxc_synth(self):
        T_calc = DetectorTranslationAlongBeam()

        stack = np.zeros([4, 512, 512], "d")
        for i in range(4):
            stack[i, 200 - i * 10, 200 - i * 10] = 1
        stack = scipy.ndimage.filters.gaussian_filter(stack, [0, 10, 10.0]) * 100
        x, y = np.meshgrid(np.arange(stack.shape[-1]), np.arange(stack.shape[-2]))
        for i in range(4):
            xc = x - (250 + i * 1.234)
            yc = y - (250 + i * 1.234 * 2)
            stack[i] += np.exp(-(xc * xc + yc * yc) * 0.5)
        shifts_v, shifts_h, found_shifts_list = T_calc.find_shift(
            stack, np.array([0.0, 1, 2, 3]), high_pass=1.0, return_shifts=True
        )

        message = "Found shifts per units %s and reference %s do not coincide" % (
            (shifts_v, shifts_h),
            (-1.234 * 2, -1.234),
        )
        assert np.all(np.isclose((shifts_v, shifts_h), (-1.234 * 2, -1.234), atol=self.abs_tol)), message
