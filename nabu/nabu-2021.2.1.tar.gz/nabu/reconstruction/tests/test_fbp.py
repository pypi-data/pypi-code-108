import numpy as np
import pytest
from scipy.ndimage import shift
from nabu.utils import clip_circle
from nabu.testutils import get_data
from nabu.cuda.utils import __has_pycuda__, __has_cufft__
if __has_pycuda__:
    from nabu.reconstruction.fbp import Backprojector


@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.sino_512 = get_data("mri_sino500.npz")["data"]
    cls.ref_512 = get_data("mri_rec_astra.npz")["data"]
    cls.sino_511 = cls.sino_512[:, :-1]
    cls.tol = 5e-2

@pytest.mark.skipif(not(__has_pycuda__ and __has_cufft__), reason="Need pycuda and scikit-cuda for this test")
@pytest.mark.usefixtures('bootstrap')
class TestFBP:

    @staticmethod
    def clip_to_inner_circle(img, radius_factor=0.99):
        radius = int(radius_factor * max(img.shape)/2)
        return clip_circle(img, radius=radius)

    def test_fbp_512(self):
        """
        Simple test of a FBP on a 512x512 slice
        """
        B = Backprojector((500, 512))
        res = B.fbp(self.sino_512)

        delta_clipped = self.clip_to_inner_circle(res - self.ref_512)
        err_max = np.max(np.abs(delta_clipped))

        assert err_max < self.tol, "Max error is too high"


    def test_fbp_511(self):
        """
        Test FBP of a 511x511 slice where the rotation axis is at (512-1)/2.0
        """
        B = Backprojector((500, 511), rot_center=255.5)
        res = B.fbp(self.sino_511)
        ref = self.ref_512[:-1, :-1]

        delta_clipped = self.clip_to_inner_circle(res - ref)
        err_max = np.max(np.abs(delta_clipped))

        assert err_max < self.tol, "Max error is too high"


    def test_fbp_roi(self):
        """
        Test FBP in region of interest
        """
        sino = self.sino_511
        B0 = Backprojector(sino.shape, rot_center=255.5)
        ref = B0.fbp(sino)

        def backproject_roi(roi, reference):
            B = Backprojector(sino.shape, rot_center=255.5, slice_roi=roi)
            res = B.fbp(sino)
            err_max = np.max(np.abs(res - ref))
            return err_max

        cases = {
            # Test 1: use slice_roi=(0, -1, 0, -1), i.e plain FBP of whole slice
            1: [(0, None, 0, None), ref],
            # Test 2: horizontal strip
            2: [(0, None, 50, 100), ref[50:100, :]],
            # Test 3: vertical strip
            3: [(60, 65, 0, None), ref[:, 60:65]],
            # Test 4: rectangular inner ROI
            4: [(157, 162, 260, -10), ref[260:-10, 157:162]],
        }
        for roi, ref in cases.values():
            err_max = backproject_roi(roi, ref)
            assert err_max < self.tol, str("backproject_roi: max error is too high for ROI=%s" % str(roi))


    def test_fbp_axis_corr(self):
        """
        Test the "axis correction" feature
        """
        sino = self.sino_512
        # Create a sinogram with a drift in the rotation axis
        def create_drifted_sino(sino, drifts):
            out = np.zeros_like(sino)
            for i in range(sino.shape[0]):
                out[i] = shift(sino[i], drifts[i])
            return out
        drifts = np.linspace(0, 20, sino.shape[0])
        sino = create_drifted_sino(sino, drifts)
        B = Backprojector(sino.shape, extra_options={"axis_correction": drifts})
        res = B.fbp(sino)

        delta_clipped = clip_circle(res - self.ref_512, radius=200)
        err_max = np.max(np.abs(delta_clipped))
        # Max error is relatively high, migh be due to interpolation of scipy shift in sinogram
        assert err_max < 10., "Max error is too high"


    def test_fbp_clip_circle(self):
        """
        Test the "clip outer circle" parameter in (extra options)
        """
        sino = self.sino_512

        for rot_center in [None, sino.shape[1]/2. - 10, sino.shape[1]/2. + 15]:
            B = Backprojector(
                sino.shape,
                rot_center=rot_center,
                extra_options={"clip_outer_circle": True}
            )
            res = B.fbp(sino)

            B0 = Backprojector(
                sino.shape,
                rot_center=rot_center,
                extra_options={"clip_outer_circle": False}
            )
            res_noclip = B0.fbp(sino)
            ref = self.clip_to_inner_circle(res_noclip, radius_factor=1)

            err_max = np.max(np.abs(res - ref))

            assert err_max < 1e-5, "Max error is too high"


    def test_fbp_centered_axis(self):
        """
        Test the "centered_axis" parameter (in extra options)
        """
        sino = np.pad(self.sino_512, ((0, 0), (100, 0)))
        rot_center = (self.sino_512.shape[1] - 1)/2. + 100

        B0 = Backprojector(self.sino_512.shape)
        ref = B0.fbp(self.sino_512)

        # Check that "centered_axis" worked
        B = Backprojector(
            sino.shape,
            rot_center=rot_center,
            extra_options={
                "centered_axis": True
            }
        )
        res = B.fbp(sino)
        # The outside region (outer circle) is different as "res" is a wider slice
        diff = self.clip_to_inner_circle(res[50:-50, 50:-50] - ref)
        np.save("/tmp/diff.npy", diff)
        err_max = np.max(np.abs(diff))
        assert err_max < 5e-2, "centered_axis without clip_circle: something wrong"

        # Check that "clip_outer_circle" works when used jointly with "centered_axis"
        B = Backprojector(
            sino.shape,
            rot_center=rot_center,
            extra_options={
                "centered_axis": True,
                "clip_outer_circle": True,
            }
        )
        res2 = B.fbp(sino)
        diff = res2 - self.clip_to_inner_circle(res, radius_factor=1)
        err_max = np.max(np.abs(diff))
        assert err_max < 1e-5, "centered_axis with clip_circle: something wrong"

