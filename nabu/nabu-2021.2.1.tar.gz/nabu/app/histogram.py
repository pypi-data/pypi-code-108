from os import path
import posixpath
from silx.io.url import DataUrl
from silx.io.dictdump import h5todict
from ..utils import check_supported
from ..io.utils import get_first_hdf5_entry, get_h5_value
from ..io.writer import NXProcessWriter
from ..misc.histogram import PartialHistogram, VolumeHistogram, hist_as_2Darray
from ..misc.histogram_cuda import CudaVolumeHistogram
from ..resources.logger import Logger, LoggerOrPrint
from .utils import parse_params_values
from .cli_configs import HistogramConfig


class VolumesHistogram:
    """
    A class for extracting or computing histograms of one or several volumes.
    """

    available_backends = {
        "numpy": VolumeHistogram,
        "cuda": CudaVolumeHistogram,
    }

    def __init__(
        self,
        fnames,
        output_file,
        chunk_size_slices=100,
        chunk_size_GB=None,
        nbins=1e6,
        logger=None,
        backend="cuda"
    ):
        """
        Initialize a VolumesHistogram object.

        Parameters
        -----------
        fnames: list of str
            List of paths to HDF5 files.
            To specify an entry for each file name, use the "?" separator:
            /path/to/file.h5?entry0001
        output_file: str
            Path to the output file
        write_histogram_if_computed: bool, optional
            Whether to write histograms that are computed to a file.
            Some volumes might be missing their histogram. In this case, the histogram
            is computed, and the result is written to a dedicated file in the same
            directory as 'output_file'.
            Default is True.
        """
        self._get_files_and_entries(fnames)
        self.chunk_size_slices = chunk_size_slices
        self.chunk_size_GB = chunk_size_GB
        self.nbins = nbins
        self.logger = LoggerOrPrint(logger)
        self.output_file = output_file
        self._get_histogrammer_backend(backend)


    def _get_files_and_entries(self, fnames):
        res_fnames = []
        res_entries = []
        for fname in fnames:
            if "?" not in fname:
                entry = None
            else:
                fname, entry = fname.split("?")
                if entry == "":
                    entry = None
            res_fnames.append(fname)
            res_entries.append(entry)
        self.fnames = res_fnames
        self.entries = res_entries


    def _get_histogrammer_backend(self, backend):
        check_supported(backend, self.available_backends.keys(), "histogram backend")
        self.VolumeHistogramClass = self.available_backends[backend]


    def _get_config_onevolume(self, fname, entry, data_shape):
        return {
            "chunk_size_slices": self.chunk_size_slices,
            "chunk_size_GB": self.chunk_size_GB,
            "bins": self.nbins,
            "filename": fname,
            "entry": entry,
            "volume_shape": data_shape,
        }


    def _get_config(self):
        conf = self._get_config_onevolume("", "", None)
        conf.pop("filename")
        conf.pop("entry")
        conf["filenames"] = self.fnames
        conf["entries"] = [entry if entry is not None else "None" for entry in self.entries]
        return conf


    def _write_histogram_onevolume(self, fname, entry, histogram, data_shape):
        output_file = path.join(
            path.dirname(self.output_file),
            path.splitext(path.basename(fname))[0]
        ) + "_histogram" + path.splitext(fname)[1]
        self.logger.info(
            "Writing histogram of %s into %s" % (fname, output_file)
        )
        writer = NXProcessWriter(output_file, entry, filemode="w", overwrite=True)
        writer.write(
            hist_as_2Darray(histogram),
            "histogram",
            config=self._get_config_onevolume(fname, entry, data_shape)
        )


    def get_histogram_single_volume(self, fname, entry, write_histogram_if_computed=True, return_config=False):
        entry = entry or get_first_hdf5_entry(fname)
        hist_path = posixpath.join(entry, "histogram" , "results", "data")
        hist_cfg_path = posixpath.join(entry, "histogram" , "configuration")
        rec_path = posixpath.join(entry, "reconstruction", "results" , "data")
        rec_url = DataUrl(file_path=fname, data_path=rec_path)
        hist = get_h5_value(fname, hist_path)
        config = None
        if hist is None:
            self.logger.info("No histogram found in %s, computing it" % fname)
            vol_histogrammer = self.VolumeHistogramClass(
                rec_url,
                chunk_size_slices=self.chunk_size_slices,
                chunk_size_GB=self.chunk_size_GB,
                nbins=self.nbins,
                logger=self.logger
            )
            hist = vol_histogrammer.compute_volume_histogram()
            if write_histogram_if_computed:
                self._write_histogram_onevolume(
                    fname, entry, hist, vol_histogrammer.data_shape
                )
            else:
                if return_config:
                    raise ValueError("return_config must be set to True to get configuration for non-existing histograms")
            hist = hist_as_2Darray(hist)
        config = h5todict(
            path.splitext(fname)[0] + "_histogram" + path.splitext(fname)[1],
            path=hist_cfg_path
        )
        if return_config:
            return hist, config
        else:
            return hist


    def get_histogram(self, return_config=False):
        histograms = []
        configs = []
        for fname, entry in zip(self.fnames, self.entries):
            self.logger.info("Getting histogram for %s" % fname)
            hist, conf = self.get_histogram_single_volume(fname, entry, return_config=True)
            histograms.append(hist)
            configs.append(conf)
        self.logger.info("Merging histograms")
        histogrammer = PartialHistogram(method="fixed_bins_number", num_bins=self.nbins)
        hist = histogrammer.merge_histograms(histograms, dont_truncate_bins=True)
        if return_config:
            return hist, configs
        else:
            return hist


    def merge_histograms_configurations(self, configs):
        if configs is None or len(configs) == 0:
            return
        res_config = {"volume_shape": list(configs[0]["volume_shape"])}
        res_config["volume_shape"][0] = 0
        for conf in configs:
            nz, ny, nx = conf["volume_shape"]
            res_config["volume_shape"][0] += nz
        res_config["volume_shape"] = tuple(res_config["volume_shape"])
        return res_config


    def write_histogram(self, hist, config=None):
        self.logger.info("Writing final histogram to %s" % (self.output_file))
        config = config or {}
        base_config = self._get_config()
        base_config.pop("volume_shape")
        config.update(base_config)
        writer = NXProcessWriter(self.output_file, "entry0000", filemode="w", overwrite=True)
        writer.write(
            hist_as_2Darray(hist),
            "histogram",
            config=config
        )


def histogram_cli():
    args = parse_params_values(
        HistogramConfig,
        parser_description="Extract/compute histogram of volume(s)."
    )
    logger = Logger(
        "nabu_histogram", level=args["loglevel"], logfile="nabu_histogram.log"
    )
    output = args["output_file"].split("?")[0]
    if path.exists(output):
        logger.fatal("Output file %s already exists, not overwriting it" % output)
        exit(1)
    chunk_size_gb = float(args["chunk_size_GB"])
    if chunk_size_gb <= 0:
        chunk_size_gb = None
    histogramer = VolumesHistogram(
        args["h5_file"],
        output,
        chunk_size_slices=int(args["chunk_size_slices"]),
        chunk_size_GB=chunk_size_gb,
        nbins=int(args["bins"]),
        logger=logger
    )
    hist, configs = histogramer.get_histogram(return_config=True)
    config = histogramer.merge_histograms_configurations(configs)
    histogramer.write_histogram(hist, config=config)


if __name__ == "__main__":
    histogram_cli()
