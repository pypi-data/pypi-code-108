import os
import numpy as np
from silx.io import get_data
from silx.io.url import DataUrl
from tomoscan.esrf.edfscan import EDFTomoScan
from tomoscan.esrf.hdf5scan import HDF5TomoScan

from ..utils import deprecation_warning, check_supported
from ..io.utils import get_compacted_dataslices
from .utils import is_hdf5_extension, get_values_from_file
from .logger import LoggerOrPrint

# Wait for next tomoscan release to ship "nexus_version"
from packaging.version import parse as parse_version
from tomoscan.version import version as tomoscan_version
_tomoscan_has_nxversion = parse_version(tomoscan_version) > parse_version("0.6.0")
#


class DatasetAnalyzer:

    _scanner = None
    kind = "none"

    """
    Base class for datasets analyzers.
    """
    def __init__(self, location, processes_file=None, extra_options=None, logger=None):
        """
        Initialize a Dataset analyzer.

        Parameters
        ----------
        location: str
            Dataset location (directory or file name)
        processes_file: str, optional
            Processes file providing supplementary information (ex. pre-processed data)
        extra_options: dict, optional
            Extra options on how to interpret the dataset.
        logger: logging object, optional
            Logger. If not set, messages will just be printed in stdout.
        """
        # COMPAT.
        if processes_file is not None:
            deprecation_warning(
                "Parameter 'processes_file' is deprecated and will be removed in a future version",
                do_print=True,
                func_name="dataset_analyzer_init"
            )
        # ---
        self.logger = LoggerOrPrint(logger)
        self.location = location
        self._set_extra_options(extra_options)
        self._get_excluded_projections()
        self._set_default_dataset_values()
        self._init_dataset_scan()
        self._finish_init()


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        # COMPAT.
        advanced_options = {
            "force_flatfield": False,
            "output_dir": None,
            "exclude_projections": None,
            "hdf5_entry": None,
        }
        if _tomoscan_has_nxversion:
            advanced_options["nx_version"] = 1.0
        # --
        advanced_options.update(extra_options)
        self.extra_options = advanced_options

    def _get_excluded_projections(self):
        excluded_projs = self.extra_options["exclude_projections"]
        if excluded_projs is None:
            return
        projs_idx = get_values_from_file(excluded_projs, any_size=True).astype(np.int32).tolist()
        self.logger.info("Ignoring projections: %s" % (str(projs_idx)))
        self.extra_options["exclude_projections"] = projs_idx


    def _init_dataset_scan(self, **kwargs):
        if self._scanner is None:
            raise ValueError("Base class")
        if self._scanner is HDF5TomoScan:
            if self.extra_options.get("hdf5_entry", None) is not None:
                kwargs["entry"] = self.extra_options["hdf5_entry"]
            if self.extra_options.get("nx_version", None) is not None:
                kwargs["nx_version"] = self.extra_options["nx_version"]
        if self._scanner is EDFTomoScan:
            # Assume 1 frame per file (otherwise too long to open each file)
            kwargs["n_frames"] = 1
        self.dataset_scanner = self._scanner(
            self.location,
            ignore_projections=self.extra_options["exclude_projections"],
            **kwargs
        )
        self.projections = self.dataset_scanner.projections
        self.flats = self.dataset_scanner.flats
        self.darks = self.dataset_scanner.darks
        self.n_angles = len(self.dataset_scanner.projections)
        self.radio_dims = (self.dataset_scanner.dim_1, self.dataset_scanner.dim_2)
        self._radio_dims_notbinned = self.radio_dims # COMPAT


    def _finish_init(self):
        pass

    def _set_default_dataset_values(self):
        self._detector_tilt = None
        self._binning = (1, 1)
        self.translations = None
        self.ctf_translations = None
        self.axis_position = None
        self._rotation_angles = None

    @property
    def energy(self):
        """
        Return the energy in kev.
        """
        return self.dataset_scanner.energy

    @property
    def distance(self):
        """
        Return the sample-detector distance in meters.
        """
        return abs(self.dataset_scanner.distance)

    @property
    def pixel_size(self):
        """
        Return the pixel size in microns.
        """
        raise ValueError("Must be implemented by inheriting class")

    @property
    def binning(self):
        """
        Return the binning in (x, y)
        """
        return self._binning

    def _get_rotation_angles(self):
        return self._rotation_angles # None by default

    @property
    def rotation_angles(self):
        """
        Return the rotation angles in radians.
        """
        return self._get_rotation_angles()

    @rotation_angles.setter
    def rotation_angles(self, angles):
        self._rotation_angles = angles

    def _is_halftomo(self):
        return None # base class

    @property
    def is_halftomo(self):
        """
        Indicates whether the current dataset was performed with half acquisition.
        """
        return self._is_halftomo()


    @property
    def detector_tilt(self):
        """
        Return the detector tilt in degrees
        """
        return self._detector_tilt


    @detector_tilt.setter
    def detector_tilt(self, tilt):
        self._detector_tilt = tilt


class EDFDatasetAnalyzer(DatasetAnalyzer):
    """
    EDF Dataset analyzer for legacy ESRF acquisitions
    """
    _scanner = EDFTomoScan
    kind = "edf"

    def _finish_init(self):
        self.remove_unused_radios()

    def _finish_init(self):
        self.remove_unused_radios()

    def remove_unused_radios(self):
        """
        Remove "unused" radios.
        This is used for legacy ESRF scans.
        """
        # Extraneous projections are assumed to be on the end
        projs_indices = sorted(self.projections.keys())
        used_radios_range = range(projs_indices[0], len(self.projections))
        radios_not_used = []
        for idx in self.projections.keys():
            if idx not in used_radios_range:
                radios_not_used.append(idx)
        for idx in radios_not_used:
            self.projections.pop(idx)
        return radios_not_used


    def _get_flats_darks(self):
        return

    @property
    def pixel_size(self):
        """
        Return the pixel size in microns.
        """
        # TODO X and Y pixel size
        return self.dataset_scanner.pixel_size * 1e6


    @property
    def hdf5_entry(self):
        """
        Return the HDF5 entry of the current dataset.
        Not applicable for EDF (return None)
        """
        return None


    def _is_halftomo(self):
        return None


class HDF5DatasetAnalyzer(DatasetAnalyzer):
    """
    HDF5 dataset analyzer
    """
    _scanner = HDF5TomoScan
    kind = "hdf5"


    def _get_rotation_angles(self):
        if self._rotation_angles is None:
            angles = np.array(self.dataset_scanner.rotation_angle)
            projs_idx = np.array(list(self.projections.keys()))
            angles = angles[projs_idx]
            self._rotation_angles = np.deg2rad(angles)
        return self._rotation_angles


    def _get_dataset_hdf5_url(self):
        if len(self.projections) > 0:
            frames_to_take = self.projections
        elif len(self.flats) > 0:
            frames_to_take = self.flats
        elif len(self.darks) > 0:
            frames_to_take = self.darks
        else:
            raise ValueError("No projections, no flats and no darks ?!")
        first_proj_idx = sorted(frames_to_take.keys())[0]
        first_proj_url = frames_to_take[first_proj_idx]
        return DataUrl(
            file_path=first_proj_url.file_path(),
            data_path=first_proj_url.data_path(),
            data_slice=None
        )


    @property
    def dataset_hdf5_url(self):
        return self._get_dataset_hdf5_url()


    @property
    def pixel_size(self):
        """
        Return the pixel size in microns.
        """
        # TODO X and Y pixel size
        try:
            xs, yz = self.dataset_scanner._get_x_y_magnified_pixel_values()
            ps = xs * 1e6
        except:
            ps = self.dataset_scanner.pixel_size * 1e6
        return ps


    @property
    def hdf5_entry(self):
        """
        Return the HDF5 entry of the current dataset
        """
        return self.dataset_scanner.entry


    def _is_halftomo(self):
        try:
            is_halftomo = self.dataset_scanner.field_of_view.value.lower() == "half"
        except:
            is_halftomo = None
        return is_halftomo


    def get_data_slices(self, what):
        """
        Return indices in the data volume where images correspond to a given kind.

        Parameters
        ----------
        what: str
            Which keys to get. Can be "projections", "flats", "darks"

        Returns
        --------
        slices: list of slice
            A list where each item is a slice.
        """
        check_supported(what, ["projections", "flats", "darks"], "image type")
        images = getattr(self, what)
        # we can't directly use set() on slice() object (unhashable). Use tuples
        tuples_list = list(set(
            (du.data_slice().start, du.data_slice().stop)
            for du in get_compacted_dataslices(images).values()
        ))
        slices_list = [slice(item[0], item[1]) for item in tuples_list]
        return slices_list



def analyze_dataset(dataset_path, processes_file=None, extra_options=None, logger=None):
    # COMPAT.
    if processes_file is not None:
        deprecation_warning(
            "Parameter 'processes_file' is deprecated and will be removed in a future version",
            do_print=True,
            func_name="dataset_analyzer_init"
        )
    # ---

    if not(os.path.isdir(dataset_path)):
        if not(os.path.isfile(dataset_path)):
            raise ValueError("Error: %s no such file or directory" % dataset_path)
        if not(is_hdf5_extension(os.path.splitext(dataset_path)[-1].replace(".", ""))):
            raise ValueError("Error: expected a HDF5 file")
        dataset_analyzer_class = HDF5DatasetAnalyzer
    else: # directory -> assuming EDF
        dataset_analyzer_class = EDFDatasetAnalyzer
    dataset_structure = dataset_analyzer_class(
        dataset_path,
        extra_options=extra_options,
        logger=logger
    )
    return dataset_structure



def get_0_180_radios(dataset_info, angles=None, return_indices=False):
    """
    Get the radios at 0 degres and 180 degrees.

    Parameters
    ----------
    dataset_info: `DatasetAnalyzer` instance
        Data structure with the dataset information
    angles: array, optional
        Array with the rotation angles. If provided, it overwrites the information from 'dataset_info', if any.
    return_indices: bool, optional
        Whether to return radios indices along with the radios array.

    Returns
    -------
    res: array or tuple
        If return_indices is True, return a tuple (radios, indices).
        Otherwise, return an array with the radios.
    """
    # COMPAT.
    if angles is None:
        angles = dataset_info.rotation_angles
    else:
        deprecation_warning(
            "The parameter 'angle' is deprecated and will throw an error in a future version",
            func_name="get_0_180_radios"
        )
    # ---
    radios_indices = []
    radios_indices = sorted(dataset_info.projections.keys())
    angles = angles - angles.min()
    i_0 = np.argmin(np.abs(angles))
    i_180 = np.argmin(np.abs(angles - np.pi))
    _min_indices = [i_0, i_180]
    radios_indices = [
        radios_indices[i_0],
        radios_indices[i_180]
    ]
    n_radios = 2
    radios = np.zeros((n_radios, ) + dataset_info.radio_dims[::-1], "f")
    for i in range(n_radios):
        radio_idx = radios_indices[i]
        radios[i] = get_data(dataset_info.projections[radio_idx]).astype("f")
    if return_indices:
        return radios, radios_indices
    else:
        return radios
