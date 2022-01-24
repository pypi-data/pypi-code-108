from math import log2, ceil
import numpy as np
from tomoscan.io import HDF5File
from ..utils import check_supported
from ..resources.logger import LoggerOrPrint

class PartialHistogram:
    """
    A class for computing histogram progressively.

    In certain cases, it is cumbersome to compute a histogram directly on a big chunk of
    data (ex. data not fitting in memory, disk access too slow) while some parts of the
    data are readily available in-memory.
    """

    histogram_methods = [
        "fixed_bins_width",
        "fixed_bins_number"
    ]

    bin_width_policies = [
        "uint16",
    ]


    def __init__(self, method="fixed_bins_width", bin_width="uint16", num_bins=None, min_bins=None):
        """
        Initialize a PartialHistogram class.

        Parameters
        ----------
        method: str, optional
            Partial histogram computing method. Available are:
               - `fixed_bins_width`: all the histograms are computed with the same bin
                 width. The class adapts to the data range and computes the number of
                 bins accordingly.
               - `fixed_bins_number`: all the histograms are computed with the same
                 number of bins. The class adapts to the data range and computes the
                 bin width accordingly.
            Default is "fixed_bins_width"
        bin_width: str or float, optional
            Policy for histogram bins when method="fixed_bins_width". Available are:
               - "uint16": The bin width is computed so that floating-point elements
               `f1` and `f2` satisfying `|f1 - f2| < bin_width` implies
               `f1_converted - f2_converted < 1` once cast to uint16.
               - A number: all the bins have this fixed width.
            Default is "uint16"
        num_bins: int, optional
            Number of bins when method = 'fixed_bins_number'.
        min_bins: int, optional
            Minimum number of bins when method = 'fixed_bins_width'.
        """
        check_supported(method, self.histogram_methods, "histogram computing method")
        self.method = method
        self._set_bin_width(bin_width)
        self._set_num_bins(num_bins)
        self.min_bins = min_bins
        self._set_histogram_methods()


    def _set_bin_width(self, bin_width):
        if self.method == "fixed_bins_number":
            self.bin_width = None
            return
        if isinstance(bin_width, str):
            check_supported(bin_width, self.bin_width_policies, "bin width policy")
            self._fixed_bw = False
        else:
            bin_width = float(bin_width)
            self._fixed_bw = True
        self.bin_width = bin_width


    def _set_num_bins(self, num_bins):
        if self.method == "fixed_bins_width":
            self.num_bins = None
            return
        if self.method == "fixed_bins_number" and num_bins is None:
            raise ValueError("Need to specify num_bins for method='fixed_bins_number'")
        self.num_bins = int(num_bins)


    def _set_histogram_methods(self):
        self._histogram_methods = {
            "fixed_bins_number": {
                "compute": self._compute_histogram_fixed_nbins,
                "merge": self._merge_histograms_fixed_nbins,
            },
            "fixed_bins_width": {
                "compute": self._compute_histogram_fixed_bw,
                "merge": self._merge_histograms_fixed_bw,
            },
        }
        assert set(self._histogram_methods.keys()) == set(self.histogram_methods)


    @staticmethod
    def _get_histograms_and_bins(histograms, center=False, dont_truncate_bins=False):
        histos = [h[0] for h in histograms]
        if dont_truncate_bins:
            bins = [h[1] for h in histograms]
        else:
            if center:
                bins = [0.5 * (h[1][1:] + h[1][:-1]) for h in histograms]
            else:
                bins = [h[1][:-1] for h in histograms]
        return histos, bins

    #
    # Histogram with fixed number of bins
    #

    def _compute_histogram_fixed_nbins(self, data, data_range=None):
        if data.ndim > 1:
            data = data.ravel()
        dmin, dmax = data.min(), data.max() if data_range is None else data_range
        res = np.histogram(data, bins=self.num_bins)
        return res


    def _merge_histograms_fixed_nbins(self, histograms, dont_truncate_bins=False):
        histos, bins = self._get_histograms_and_bins(
            histograms, dont_truncate_bins=dont_truncate_bins
        )
        res = np.histogram(
            np.hstack(bins),
            weights=np.hstack(histos),
            bins=self.num_bins,
        )
        return res

    #
    # Histogram with fixed bin width
    #

    def _bin_width_u16(self, dmin, dmax):
        return (dmax - dmin) / 65535.


    def _bin_width_fixed(self, dmin, dmax):
        return self.bin_width


    def get_bin_width(self, dmin, dmax):
        if self._fixed_bw:
            return self._bin_width_fixed(dmin, dmax)
        elif self.bin_width == "uint16":
            return self._bin_width_u16(dmin, dmax)
        else:
            raise ValueError()


    def _compute_histogram_fixed_bw(self, data, data_range=None):
        dmin, dmax = data.min(), data.max() if data_range is None else data_range
        min_bins = self.min_bins or 1
        bw_max = self.get_bin_width(dmin, dmax)
        nbins = 0
        bw_factor = 1
        while nbins < min_bins:
            bw = 2**round(log2(bw_max)) / bw_factor
            nbins = int((dmax - dmin)/bw)
            bw_factor *= 2
        res = np.histogram(data, bins=nbins)
        return res


    def _merge_histograms_fixed_bw(self, histograms, **kwargs):
        histos, bins = self._get_histograms_and_bins(histograms, center=False)
        dmax = max([b[-1] for b in bins])
        dmin = min([b[0] for b in bins])
        bw_max = max([b[1] - b[0] for b in bins])
        res = np.histogram(
            np.hstack(bins),
            weights=np.hstack(histos),
            bins=int((dmax - dmin)/bw_max)
        )
        return res

    #
    # Dispatch methods
    #

    def compute_histogram(self, data, data_range=None):
        compute_hist_func = self._histogram_methods[self.method]["compute"]
        return compute_hist_func(data, data_range=data_range)


    def merge_histograms(self, histograms, **kwargs):
        merge_hist_func = self._histogram_methods[self.method]["merge"]
        return merge_hist_func(histograms, **kwargs)


class VolumeHistogram:
    """
    A class for computing the histogram of an entire volume.
    Unless explicitly specified, histogram is computed in several passes so that not
    all the volume is loaded in memory.
    """

    def __init__(self, data_url, chunk_size_slices=100, chunk_size_GB=None, nbins=1e6, logger=None):
        """
        Initialize a VolumeHistogram object.

        Parameters
        ----------
        fname: DataUrl
            DataUrl to the HDF5 file.
        chunk_size_slices: int, optional
            Compute partial histograms of groups of slices. This is the default behavior,
            where the groups size is 100 slices.
            This parameter is mutually exclusive with 'chunk_size_GB'.
        chunk_size_GB: float, optional
            Maximum memory (in GB) to use when computing the histogram by group of slices.
            This parameter is mutually exclusive with 'chunk_size_slices'.
        nbins: int, optional
            Histogram number of bins. Default is 1e6.
        """
        self.data_url = data_url
        self.logger = LoggerOrPrint(logger)
        self._get_data_info()
        self._set_chunk_size(chunk_size_slices, chunk_size_GB)
        self.nbins = int(nbins)
        self._init_histogrammer()


    def _get_data_info(self):
        self.fname = self.data_url.file_path()
        self.data_path = self.data_url.data_path()
        with HDF5File(self.fname, "r") as fid:
            try:
                data_ptr = fid[self.data_path]
            except KeyError:
                msg = str(
                    "Could not access HDF5 path %s in file %s. Please check that this file \
                    actually contains a reconstruction and that the HDF5 entry %s is correct"
                    % (self.data_path, self.fname, self.entry)
                )
                self.logger.fatal(msg)
                raise ValueError(msg)
            if data_ptr.ndim != 3:
                msg = "Expected data to have 3 dimensions, got %d" % data_ptr.ndim
                raise ValueError(msg)
            self.data_shape = data_ptr.shape
            self.data_dtype = data_ptr.dtype
            self.data_nbytes_GB = np.prod(data_ptr.shape) * data_ptr.dtype.itemsize / 1e9


    def _set_chunk_size(self, chunk_size_slices, chunk_size_GB):
        if not((chunk_size_slices is not None) ^ (chunk_size_GB is not None)):
            raise ValueError("Please specify either chunk_size_slices or chunk_size_GB")
        if chunk_size_slices is None:
            chunk_size_slices = int(
            chunk_size_GB / (np.prod(self.data_shape[1:]) * self.data_dtype.itemsize / 1e9)
        )
        self.chunk_size = chunk_size_slices
        self.logger.debug("Computing histograms by groups of %d slices" % self.chunk_size)


    def _init_histogrammer(self):
        self.histogrammer = PartialHistogram(
            method="fixed_bins_number", num_bins=self.nbins
        )


    def _compute_histogram(self, data):
        return self.histogrammer.compute_histogram(data.ravel()) # 1D


    def compute_volume_histogram(self):
        n_z = self.data_shape[0]
        histograms = []
        n_steps = ceil(n_z / self.chunk_size)
        with HDF5File(self.fname, "r") as fid:
            for chunk_id in range(n_steps):
                self.logger.debug("Computing histogram %d/%d" % (chunk_id+1, n_steps))
                z_slice = slice(
                    chunk_id * self.chunk_size,
                    (chunk_id + 1 )* self.chunk_size
                )
                images_stack = fid[self.data_path][z_slice, :, :]
                hist = self._compute_histogram(images_stack)
                histograms.append(hist)
        res = self.histogrammer.merge_histograms(histograms)
        return res



def hist_as_2Darray(hist, center=True, dtype="f"):
    hist, bins = hist
    if bins.size != hist.size:
        # assert bins.size == hist.size +1
        if center:
            bins = 0.5 * (bins[1:] + bins[:-1])
        else:
            bins = bins[:-1]
    res = np.zeros((2, hist.size), dtype=dtype)
    res[0] = hist
    res[1] = bins.astype(dtype)
    return res


def add_last_bin(histo_bins):
    """
    Add the last bin (max value) to a list of bin edges.
    """
    res = np.zeros(histo_bins.size + 1, dtype=histo_bins.dtype)
    res[:-1] = histo_bins[:]
    res[-1] = res[-2] + (res[1] - res[0])
    return res
