from os import path
from tempfile import mkdtemp
import pytest
import numpy as np
from nabu.testutils import get_data
from nabu.misc.histogram import PartialHistogram
from nabu.misc.histogram_cuda import CudaPartialHistogram, __has_pycuda__
if __has_pycuda__:
    import pycuda.gpuarray as garray


@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.data = get_data("mri_rec_astra.npz")["data"]
    cls.data /= 10
    cls.data[:100] *= 10
    cls.data_part_1 = cls.data[:100]
    cls.data_part_2 = cls.data[100:]
    cls.data0 = cls.data.ravel()
    cls.bin_tol = 1e-5 * (cls.data0.max() - cls.data0.min())
    cls.hist_rtol = 1.5e-3


@pytest.mark.usefixtures('bootstrap')
class TestPartialHistogram:

    def compare_histograms(self, hist1, hist2):
        errmax_bins = np.max(np.abs(hist1[1] - hist2[1]))
        assert errmax_bins < self.bin_tol
        errmax_hist = np.max(np.abs(hist1[0] - hist2[0])/hist2[0].max())
        assert errmax_hist/hist2[0].max() < self.hist_rtol

    def test_fixed_nbins(self):
        partial_hist = PartialHistogram(method="fixed_bins_number", num_bins=1e6)
        hist1 = partial_hist.compute_histogram(self.data_part_1.ravel())
        hist2 = partial_hist.compute_histogram(self.data_part_2.ravel())
        hist = partial_hist.merge_histograms([hist1, hist2])
        ref = np.histogram(self.data0, bins=partial_hist.num_bins)
        self.compare_histograms(hist, ref)

    @pytest.mark.skipif(not(__has_pycuda__), reason="Need cuda/pycuda for this test")
    def test_fixed_nbins_cuda(self):
        partial_hist = CudaPartialHistogram(method="fixed_bins_number", num_bins=1e6)
        data_part_1 = garray.to_gpu(np.tile(self.data_part_1, (1, 1, 1)))
        data_part_2 = garray.to_gpu(np.tile(self.data_part_2, (1, 1, 1)))
        hist1 = partial_hist.compute_histogram(data_part_1)
        hist2 = partial_hist.compute_histogram(data_part_2)
        hist = partial_hist.merge_histograms([hist1, hist2])
        ref = np.histogram(self.data0, bins=partial_hist.num_bins)
        self.compare_histograms(hist, ref)
