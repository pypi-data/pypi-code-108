import os
from ..resources.logger import LoggerOrPrint
from ..utils import deprecation_warning, subsample_dict

class DatasetValidatorBase:
    def __init__(self, nabu_config, dataset_info, logger=None):
        """
        Perform a coupled validation of nabu configuration against dataset information.
        Check the consistency of these two structures, and modify them in-place.

        Parameters
        ----------
        nabu_config: dict
            Dictionary containing the nabu configuration, usually got from
            `nabu.pipeline.config.validate_config()`
            It will be modified !
        dataset_info: `DatasetAnalyzer` instance
            Structure containing information on the dataset to process.
            It will be modified !
        """
        self.nabu_config = nabu_config
        self.dataset_info = dataset_info
        self.logger = LoggerOrPrint(logger)
        self._validate()


    def _validate(self):
        raise ValueError("Base class")


    # COMPAT.
    @property
    def dataset_infos(self):
        deprecation_warning(
            "The name 'dataset_infos' is deprecated. Please use 'dataset_info'.",
            func_name="validator_dataset_infos_attr"
        )
        return self.dataset_info
    # ---

    @property
    def is_halftomo(self):
        do_halftomo = self.nabu_config["reconstruction"].get("enable_halftomo", False)
        if do_halftomo == "auto":
            do_halftomo = self.dataset_info.is_halftomo
            if do_halftomo is None:
                raise ValueError(
                    "'enable_halftomo' was set to 'auto' but unable to get the information on field of view"
                )
        return do_halftomo


    def _check_not_empty(self):
        if len(self.dataset_info.projections) == 0:
            msg = "Dataset seems to be empty (no projections)"
            self.logger.fatal(msg)
            raise ValueError(msg)
        if self.dataset_info.n_angles is None:
            msg = "Could not determine the number of projections. Please check the .info or HDF5 file"
            self.logger.fatal(msg)
            raise ValueError(msg)
        for dim_name, n in zip(["dim_1", "dim_2"], self.dataset_info.radio_dims):
            if n is None:
                msg = "Could not determine %s. Please check the .info file or HDF5 file" % dim_name
                self.logger.fatal(msg)
                raise ValueError(msg)
        self._projs_indices = sorted(self.dataset_info.projections.keys())


    @staticmethod
    def _convert_negative_idx(idx, last_idx):
        res = idx
        if idx < 0:
            res = last_idx + idx
        return res


    def _get_nx_ny(self, binning=1):
        if self.is_halftomo:
            cor = int(round(self.dataset_info.axis_position / binning))
            nx = self.dataset_info.radio_dims[0] // binning
            nx = max(2*cor, 2 * (nx - 1 - cor))
        else:
            nx = self.dataset_info.radio_dims[0] // binning
        ny = nx
        return nx, ny


    def _convert_negative_indices(self):
        """
        Convert any negative index to the corresponding positive index.
        """
        nx, nz = self.dataset_info.radio_dims
        ny = nx
        if self.is_halftomo:
            if self.dataset_info.axis_position is None:
                raise ValueError("Cannot use rotation axis position in the middle of the detector when half tomo is enabled")
            nx, ny = self._get_nx_ny()
        what = (
            ("reconstruction", "start_x", nx),
            ("reconstruction", "end_x", nx),
            ("reconstruction", "start_y", ny),
            ("reconstruction", "end_y", ny),
            ("reconstruction", "start_z", nz),
            ("reconstruction", "end_z", nz),
        )
        for section, key, upper_bound in what:
            val = self.nabu_config[section][key]
            if isinstance(val, str):
                idx_mapping = {
                    "first": 0,
                    "middle": upper_bound // 2, # works on both start_ and end_ since the end_ index is included
                    "last": upper_bound - 1
                }
                res = idx_mapping[val]
            else:
                res = self._convert_negative_idx(
                self.nabu_config[section][key], upper_bound
            )
            self.nabu_config[section][key] = res


    def _get_resources(self):
        opts = self.nabu_config["resources"]
        if opts["gpu_id"] != []:
            opts["gpus"] = len(opts["gpu_id"])
        if opts["gpus"] == 0:
            opts["gpu_id"] = []


    def _get_output_filename(self):
        opts = self.nabu_config["output"]
        dataset_path = self.nabu_config["dataset"]["location"]
        if opts["location"] == "" or opts["location"] is None:
            opts["location"] = os.path.dirname(dataset_path)
        if opts["file_prefix"] == "" or opts["file_prefix"] is None:
            if os.path.isfile(dataset_path): # hdf5
                file_prefix = os.path.basename(dataset_path).split(".")[0]
            elif os.path.isdir(dataset_path):
                file_prefix = os.path.basename(dataset_path)
            else:
                raise ValueError(
                    "dataset location %s is neither a file or directory"
                    % dataset_path
                )
            file_prefix += "_rec" # avoid overwriting dataset
            opts["file_prefix"] = file_prefix


    @staticmethod
    def _check_start_end_idx(start, end, n_elements, start_name="start_x", end_name="end_x"):
        assert (start >= 0 and start < n_elements), "Invalid value for %s, must be >= 0 and < %d" % (start_name, n_elements)
        assert (end >= 0 and end < n_elements), "Invalid value for %s, must be >= 0 and < %d" % (end_name, n_elements)


    # COMPAT.
    def perform_all_checks(self, remove_unused_radios=True):
        """
        Deprecated function
        """
        deprecation_warning(
            "This method is deprecated as validation is now done at class instantiation",
            func_name="perform_all_checks"
        )
    # ----


    def _handle_binning(self):
        """
        Modify the dataset description and nabu config to handle binning and
        projections subsampling.
        """
        self.dataset_info._radio_dims_notbinned = self.dataset_info.radio_dims
        dataset_cfg = self.nabu_config["dataset"]
        self.binning = (dataset_cfg["binning"], dataset_cfg["binning_z"])
        self.dataset_info._binning = self.binning
        subsampling_factor = dataset_cfg["projections_subsampling"]
        self.projections_subsampling = subsampling_factor
        self.dataset_info._projections_subsampled = self.dataset_info.projections
        self.dataset_info._projs_indices_subsampled = self._projs_indices
        if subsampling_factor > 1:
            self.dataset_info._projections_subsampled = subsample_dict(self.dataset_info.projections, subsampling_factor)
            self.dataset_info._projs_indices_subsampled = sorted(self.dataset_info._projections_subsampled.keys())
            self.dataset_info.reconstruction_angles = self.dataset_info.reconstruction_angles[::subsampling_factor]
            # should be simply len(projections)... ?
            self.dataset_info.n_angles //= subsampling_factor
        if self.binning != (1, 1):
            bin_x, bin_z = self.binning
            bin_y = bin_x # square slices
            # Update end_x, end_y, end_z
            rec_cfg = self.nabu_config["reconstruction"]
            end_x, end_y = self._get_end_xy() # Not so trivial. See function documentation
            rec_cfg["end_x"] = end_x
            rec_cfg["end_y"] = end_y
            rec_cfg["end_z"] = (rec_cfg["end_z"] + 1) // bin_z - 1
            rec_cfg["start_x"] = (rec_cfg["start_x"] // bin_x)
            rec_cfg["start_y"] = (rec_cfg["start_y"] // bin_y)
            rec_cfg["start_z"] = (rec_cfg["start_z"] // bin_z)
            # Update radio_dims
            nx, nz = self.dataset_info.radio_dims
            nx //= bin_x
            ny = nx # square slices
            nz //= bin_z
            self.dataset_info.radio_dims = (nx, nz)
            # Update the Rotation center
            # TODO axis_corrections
            rot_c = self.dataset_info.axis_position
            nx0, nz0 = self.dataset_info._radio_dims_notbinned
            bin_fact = nx0 / nx
            if rot_c is not None: # user-specified
                rot_c /= bin_fact # float
            else:
                rot_c = (nx - 1)/2.
            self.dataset_info.axis_position = rot_c


    def _check_output_file(self):
        out_cfg = self.nabu_config["output"]
        out_fname = os.path.join(out_cfg["location"], out_cfg["file_prefix"] + out_cfg["file_format"])
        if os.path.exists(out_fname):
            raise ValueError("File %s already exists" % out_fname)


    def _handle_processing_mode(self):
        mode = self.nabu_config["resources"]["method"]
        if mode == "preview":
            print("Warning: the method 'preview' was selected. This means that the data volume will be binned so that everything fits in memory.")
            # TODO automatically compute binning/subsampling factors as a function of lowest memory (GPU)
            self.nabu_config["dataset"]["binning"] = 2
            self.nabu_config["dataset"]["binning_z"] = 2
            self.nabu_config["dataset"]["projections_subsampling"] = 2
        # TODO handle other modes


    def _get_end_xy(self):
        """
        Return the "end_x" value for reconstruction, accounting for binning.

        There are three situations:

           1. Normal setting: Nx_rec = Nx
           2. Half acquisition, CoR on the right side: Nx_rec = 2 * |c|
           3. Half acquisition, CoR on the left side: Nx_rec = 2 * (Nx - 1 - |c|)

        where |c| = int(round(c)).

        **Without binnig**

        Let e0 denote the default value for "end_x", without user modification.
        By default, all the slice is reconstructed, so
            e0 = Nx_rec - 1
        Let e denote the user value for "end_x". By default e = e0, but the user might
        want to tune it.
        Let d denote the distance between e and e0: d = e0 - e. By default d = 0.

        **With binning**

        Let b denote the binning value in x.

           1. Nx' = Nx // b
           2. Nx' = 2 * |c/b|
           3. Nx' = 2 * (Nx//b - 1 - |c/b|)

        With the same notations, with a prime suffix, we have:

           * e0' = Nx' - 1  is the default value of "end_x" accounting for binning
           * e' is the user value for "end_x" accounting for binning
           * d' = e0' - e'  is the distance between e0' and e'

        In the standard setting (no half tomography), computing e' (i.e end_x) is straightforward:
        e' = (e+1)//b - 1

        With half tomography, because of the presence of |c| = int(floor(c)), the things
        are a bit more difficult.
        We enforce the following invariant in all settings:

           (I1) dist(e0', e') = dist(e0, e) // b

        Another possible invariant is

            (I2) delta_x' = delta_x // b

        Which is equivalent to (I1) only in setting (1) (i.e no half-tomography).
        In the half-tomography setting, (I1) and (I2) are not equivalent anymore, so we have
        to choose between the two.
        We believe it is more consistent to preserve "end_x", so that a user not modying "end_x"
        ends up with all the range [0, Nx - 1] reconstructed.

        Therefore:
           e' = e0' - d//b

        """
        b, _ = self.binning
        end_xy = []
        for i in range(2):
            what = ["end_x", "end_y"][i]
            e0 = self._get_nx_ny()[i] - 1
            e0p = self._get_nx_ny(binning=b)[i] - 1
            d = e0 - self.nabu_config["reconstruction"][what]
            ep = e0p - d//b
            end_xy.append(ep)
        return tuple(end_xy)

