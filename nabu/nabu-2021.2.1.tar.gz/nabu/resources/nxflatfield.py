import os
import posixpath
from tempfile import mkdtemp
import numpy as np
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from tomoscan.esrf.hdf5scan import ImageKey
from ..utils import check_supported, is_writeable, deprecation_warning
from ..io.writer import NXProcessWriter
from ..io.utils import get_first_hdf5_entry, hdf5_entry_exists, get_h5_str_value, get_compacted_dataslices
from ..thirdparty.tomwer_load_flats_darks import get_flats_frm_process_file, get_darks_frm_process_file
from .logger import LoggerOrPrint


val_to_nxkey = {
    "flats": ImageKey.FLAT_FIELD.value,
    "darks": ImageKey.DARK_FIELD.value,
    "projections": ImageKey.PROJECTION.value,
}


def _extract_entry(data_path):
    return data_path.lstrip("/").split("/")[0]


def replace_h5_entry(data_url, new_entry):
    split_path = data_url.data_path().lstrip("/").split("/")
    split_path[0] = new_entry
    new_data_path = "/".join(split_path)
    return DataUrl(
        file_path=data_url.file_path(),
        data_path=new_data_path,
        data_slice=data_url.data_slice(),
        scheme=data_url.scheme
    )


class NXFlatField:
    """
    A helper class to load flats and darks, or to compute the final ones.

    At ESRF, several darks/flats series are acquired during a scan.
    Each series undergoes a reduction (mean, median, ...) to get a "final" image.
    For example, there is one series of flats in the beginning, and one in the end ;
    thus there are two corresponding "final" flats.
    """

    _loading_modes = [None, "force-load", "force-compute"]

    def __init__(
        self, dataset_info, lookup_files=None, results_url=None,
        force_load_existing_results=False, loading_mode=None, logger=None,
        flats_reduction="mean", darks_reduction="mean",
        need_flats_and_darks=True,
    ):
        """
        Initialize a FlatFieldLoader helper.

        Parameters
        -----------
        dataset_info: DatasetAnalyzer
            A DatasetAnalyzer object
        lookup_files: list of DataUrl, optional
            List of paths (DataUrl) to inspect to load existing "final" flats/darks.
            If something is found one of these URL, the data will be loaded from there.
        results_url: silx.io.url.DataUrl, optional
            Url to where to write the results.
            Mind the difference with `lookup_files`: this parameter is for writing.
            If the file already exists, its data will be overwritten !
            If set to None, the results will not be written anywhere.
        force_load_existing_results: bool, optional
            DEPRECATED - please use the 'loading_mode' parameter instead.
            Whether to force loading existing results, regardless of the input data
            and results file.
            If set to True, the parameter 'lookup_files' must contain exactly one
            (valid) DataUrl of the results to load.
            Default is False.
        loading_mode: str, optional
            Which approach to take for generating the reduced flats/darks:

               - None (default). First attempt to load already-computed flats/darks from a file,
                 if not present, do the computations.
               - force-load: Load the flats/darks from a given file.
               - force-compute: Discard any existing file and perform the computations
        logger: Logger object, optional
            Logging object
        flats_reduction: str, optional
            Reduction function to use for flats. Can be "mean", "median" or "sum".
            Default is "mean".
        darks_reduction: str, optional
            Reduction function to use for darks. Can be "mean", "median" or "sum".
            Default is "mean".
        need_flats_and_darks: bool, optional
            Whether both flats and darks are needed to compute the final darks/flats.
            If set to True and either no flat/dark is found, an error will be raised.
            Default is True.


        Warning
        -------
        Make sure to use DataUrl objects for the 'lookup_files' and 'results_url'
        parameters.
        """
        if dataset_info.kind != "hdf5":
            raise NotImplementedError("Unsupported dataset type")
        self.dataset_info = dataset_info
        self.data_url = dataset_info.dataset_hdf5_url
        self.image_keys = dataset_info.dataset_scanner.image_key
        self.lookup_files = lookup_files or []
        self.results_url = results_url
        self._set_loading_mode(loading_mode, force_load_existing_results)
        self._need_flats_and_darks = need_flats_and_darks
        self.logger = LoggerOrPrint(logger)
        self.reduction_function = {}
        self._set_reduction_method("flats", flats_reduction)
        self._set_reduction_method("darks", darks_reduction)

        self._get_data_shape()
        self._discover_existing_results()


    def _set_loading_mode(self, mode, force_load_existing_results):
        self.force_load_existing_results = force_load_existing_results
        if force_load_existing_results:
            deprecation_warning(
                "'force_load_existing_results' is replaced with 'mode'",
                func_name="NXFlatField"
            )
        if mode is True or mode is False:
            mode = None
        check_supported(mode, self._loading_modes, "Flatfield loading mode")
        self.loading_mode = mode
        if self.loading_mode == "force-load":
            self.force_load_existing_results = True


    def _set_reduction_method(self, what, reduction_method):
        check_supported(what, val_to_nxkey.keys(), "image type")
        red_methods = {
            "mean": np.mean,
            "median": np.median,
            "sum": np.sum
        }
        check_supported(reduction_method, red_methods, "reduction method")
        self.reduction_function[what] = red_methods[reduction_method]


    def _get_data_shape(self):
        with HDF5File(self.data_url.file_path(), "r") as fid:
            shp = fid[self.data_url.data_path()].shape
        self.data_shape = shp


    def _discover_existing_results(self):
        self._existing_results = None
        if self.loading_mode == "force-compute" or self.lookup_files == []:
            return
        for data_url in self.lookup_files:
            if self.force_load_existing_results or self.is_valid_results_file(data_url):
                self._existing_results = self._get_existing_results_url(data_url)
                self.logger.info("Loaded flats/darks from %s" % data_url.file_path())
                break
        if self._existing_results is None:
            self.logger.debug("Flats/darks could not be loaded from any file")


    def get_config(self):
        if self.results_url is None:
            results_file = "None"
        else:
            results_file = self.results_url.file_path()
        return {
            "input_file": self.data_url.path(),
            "lookup_files": [url.path() for url in self.lookup_files],
            "results_file": results_file,
            "flats_reduction_method": self.reduction_function["flats"].__name__,
            "darks_reduction_method": self.reduction_function["darks"].__name__,
            "image_key": self.image_keys,
            "data_shape": self.data_shape,
        }


    def _is_same_configuration(self, cfg, ignore_filenames=False):
        my_config = self.get_config()
        res = True
        try:
            for key in ["flats_reduction_method", "darks_reduction_method"]:
                res &= (my_config[key] == get_h5_str_value(cfg[key]))

            res &= np.allclose(my_config["data_shape"], cfg["data_shape"][()])
            res &= np.allclose(my_config["image_key"], cfg["image_key"][()])
            du1 = DataUrl(path=my_config["input_file"])
            du2 = DataUrl(path=get_h5_str_value(cfg["input_file"]))
            if not(ignore_filenames):
                res &= (
                    os.path.basename(du1.file_path()) == os.path.basename(du2.file_path())
                )
            res &= (du1.data_path() == du2.data_path())
        except KeyError:
            res = False
        return res


    def is_valid_results_file(self, data_url):
        if not(os.path.isfile(data_url.file_path())):
            return False
        cfg_path = os.path.join(data_url.data_path(), "configuration")
        with HDF5File(data_url.file_path(), "r") as fid:
            try:
                cfg = fid[cfg_path]
            except KeyError:
                return False
            is_same_cfg = self._is_same_configuration(cfg)
            if not(is_same_cfg):
                self.logger.warning("Incompatible results file: %s" % data_url.file_path())
        return is_same_cfg


    def _get_existing_results_url(self, data_url):
        res = {"flats": {}, "darks": {}}
        # If entry is incorrect, take first entry
        # TODO find a more elegant mechanism
        fname = data_url.file_path()
        entry = _extract_entry(data_url.data_path())
        if not(hdf5_entry_exists(fname, entry)):
            new_entry = get_first_hdf5_entry(fname)
            data_url = replace_h5_entry(data_url, new_entry)
            self.logger.warning(
                "Entry %s in file %s does not exist. Using the first entry %s"
                % (entry, fname, new_entry)
            )
        #
        results_path = os.path.join(data_url.data_path(), "results") # NXProcess
        with HDF5File(data_url.file_path(), "r") as fid:
            for what in res.keys():
                for img_id in fid[results_path][what].keys():
                    res[what][int(img_id)] = DataUrl(
                        file_path=data_url.file_path(),
                        data_path=os.path.join(results_path, what, img_id)
                    )
        return res


    @staticmethod
    def load_data(ff_results):
        res_arrays = {"flats": {}, "darks": {}}
        for what in res_arrays.keys():
            for img_id, data_url in ff_results[what].items():
                with HDF5File(data_url.file_path(), "r") as fid:
                    res_arrays[what][img_id] = fid[data_url.data_path()][()]
        return res_arrays


    def get_data_chunk(self, data_slice):
        """
        Get a data chunk from the data volume whose path was specified at class instantiation.
        """
        with HDF5File(self.data_url.file_path(), "r", swmr=True) as f:
            data_raw = f[self.data_url.data_path()][data_slice]
        return data_raw


    def write_results(self, flats_and_darks, process_name="flat_field_images"):
        """
        Write the results in a HDF5 file.

        Parameters
        -----------
        flats_and_darks: dict
            Dictionary of dictionaries, in the form

            >>> {
            ...     "darks": { 0: reduced_flat_0, 1000: reduced_flat_1000},
            ...     "flats": { 1: reduced_dark_0},
            ... }

            where each reduced_array is a numpy array.

        process_name: str, optional
            Process name. Default is "flat_field_images".
        """
        if self.results_url is None:
            return
        results_file = self.results_url.file_path()
        writer = NXProcessWriter(
            results_file,
            entry=_extract_entry(self.results_url.data_path()),
            overwrite=True
        )
        h5_results_path = writer.write(
            flats_and_darks, process_name, config=self.get_config()
        )
        if "flats" in flats_and_darks:
            self.dataset_info.dataset_scanner.save_reduced_flats(flats_and_darks["flats"])
        if "darks" in flats_and_darks:
            self.dataset_info.dataset_scanner.save_reduced_darks(flats_and_darks["darks"])
        self.logger.info("Wrote final flats and darks to %s" % results_file)
        links = {}
        for img_type, imgs in flats_and_darks.items():
            links[img_type] = {}
            for img_idx in imgs.keys():
                links[img_type][img_idx] = DataUrl(
                    file_path=results_file,
                    data_path=os.path.join(h5_results_path, img_type, str(img_idx))
                )
        return links


    def compute_final_images(self):
        self.logger.info(
            "Computing final flats/darks for %s" % self.data_url.file_path()
        )
        res = {"flats": {}, "darks": {}}
        for what in res.keys():
            img_slices = self.dataset_info.get_data_slices(what)
            if img_slices == []:
                err_msg = "No %s found in %s" % (what, self.data_url.file_path())
                self.logger.error(err_msg)
                if self._need_flats_and_darks:
                    raise ValueError(err_msg)
                res[what] = None
            for data_slice in img_slices:
                data_chunk = self.get_data_chunk(data_slice)
                img = self.reduction_function[what](data_chunk, axis=0)
                res[what][int(data_slice.start)] = img
        return res


    def get_final_urls(self):
        if self._existing_results is not None:
            return self._existing_results
        else:
            if self.results_url is None:
                raise ValueError("Cannot call get_final_urls when results do not exist and write_results=None")
            flats_and_darks = self.compute_final_images()
            urls = self.write_results(flats_and_darks)
            return urls


def update_dataset_info_flats_darks(dataset_info, processes_file=None, output_dir=None, flatfield_mode=None):
    """
    Update a DatasetAnalyzer instance with flats/darks images.

    Parameters
    ----------
    dataset_info: DatasetAnalyzer
        DatasetAnalyzer instance
    processes_file: str, optional
        File name of a 'processes.h5' HDF5 file containing final darks/flats to use.
        If the file exists and contains the data, then darks/flats from this file will be used.
    output_dir: str, optional
        Directory where 'processes.h5' will be stored if we can't write in the same directory
        as the dataset.
    flatfield_mode: bool or str, optional
        How to perform flatfield:

           - False indicates that flatfield normalization is entirely disabled
           - True will do the flats/darks reduction by firt atttempting to load results from files
           - "force-compute" will discard files containing existing results and do the reduction
             (so the current dataset has to contain darks/flats)
           - "force-load" will load the reduced flats/darks regardless of the current dataset
             actually containing any flat/dark.
    """
    def _load_flats_from_tomwer():
        tomwer_processes_file = _get_tomwer_process_file_name()
        if tomwer_processes_file is None or not(os.path.isfile(tomwer_processes_file)):
            # if not found try with the old one
            tomwer_processes_file = os.path.join(
                dataset_info.dataset_scanner.path,
                "tomwer_processes.h5"
            )
        if tomwer_processes_file is None or not (os.path.isfile(tomwer_processes_file)):
            return False

        # try to load dark and flats from the default url (flats.hdf5 and darks.hdf5 for HDF5TomoScan and dark.edf, flatHSTXXX.edf for EDFTomoScan)
        new_flats = dataset_info.dataset_scanner.load_reduced_flats(return_as_url=True)
        new_darks = dataset_info.dataset_scanner.load_reduced_darks(return_as_url=True)

        if not (len(new_flats) > 0 and len(new_darks) > 0):
            new_flats = get_flats_frm_process_file(
                tomwer_processes_file, dataset_info.dataset_scanner.entry
            )
            new_darks = get_flats_frm_process_file(
                tomwer_processes_file, dataset_info.dataset_scanner.entry
            )

        if not (len(new_flats) > 0 and len(new_darks) > 0):
            return False

        if not (len(new_flats) > 0 and len(new_darks) > 0):
            return False
        dataset_info.logger.info("Loading darks and refs from %s" % tomwer_processes_file)
        dataset_info.flats = new_flats
        dataset_info.darks = new_darks
        return True


    def _get_results_file():
        if processes_file not in (None, ""):
            if is_writeable(os.path.dirname(processes_file)):
                return processes_file
            else:
                dataset_info.logger.error("Cannot write to %s" % processes_file)
        results_relfname = os.path.splitext(
            os.path.basename(dataset_info.dataset_scanner.master_file)
        )[0] + "_nabu_processes.hdf5"
        # Attempt 1: write in the same dir as the master NX file
        results_dir = os.path.dirname(dataset_info.dataset_scanner.master_file)
        if is_writeable(results_dir):
            return os.path.join(results_dir, results_relfname)
        # Attempt 2: write in the "output" dir, if specified
        out_dir = output_dir
        if out_dir is not None and is_writeable(out_dir):
            return os.path.join(out_dir, results_relfname)
        # Last attempt: write in a temporary directory
        tempdir = mkdtemp(prefix="nabu_flatfield_")
        return os.path.join(tempdir, results_relfname)


    def _compute_or_load_flats():
        h5_entry = dataset_info.hdf5_entry or "entry"
        h5_path = posixpath.join(h5_entry, "flat_field_images")
        # In this case, we always want to return a dict of DataUrl,
        # so we have to write the final flats/darks somewhere.
        # Therefore results_url cannot be None when instantiating NXFlatField.
        # It will be ignored if data can be loaded from processes_file
        results_file = _get_results_file()
        results_url = DataUrl(file_path=results_file, data_path=h5_path)

        lookup_files = None
        if processes_file is not None:
            lookup_files = [DataUrl(file_path=processes_file, data_path=h5_path)]
        else:
            if os.path.isfile(results_file):
                # We use an existing "results file"  as lookup file.
                # NXFlatField wont overwrite it if it has the good configuration
                lookup_files = [DataUrl(file_path=results_file, data_path=h5_path)]

        nxflatfield = NXFlatField(
            dataset_info,
            lookup_files=lookup_files,
            results_url=results_url,
            loading_mode=flatfield_mode,
            flats_reduction="median",
            darks_reduction="mean",
            logger=dataset_info.logger
        )
        res = nxflatfield.get_final_urls()
        dataset_info.flats = res["flats"]
        dataset_info.darks = res["darks"]


    def _get_tomwer_process_file_name():
        if dataset_info.dataset_scanner.path is not None:
            basename, _ = os.path.splitext(dataset_info.dataset_scanner.master_file)
            basename = os.path.basename(basename)
            basename = "_".join((basename, "tomwer_processes.h5"))
            return os.path.join(dataset_info.dataset_scanner.path, basename)
        else:
            return None


    def _get_flats_darks():
        if flatfield_mode is False:
            # Flat-fielding is disabled by user
            return
        if len(dataset_info.flats) == 0 and flatfield_mode != "force-load":
            # No flats at all in the dataset. Do nothing.
            return
        if processes_file is None and _load_flats_from_tomwer():
            # Loaded from [XXX]_tomwer_processes.h5
            return
        # Otherwise load or compute flats/darks with nabu
        _compute_or_load_flats()

    _get_flats_darks()

