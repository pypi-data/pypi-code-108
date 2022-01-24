import warnings
from shutil import copy as copy_file
from os import path
from h5py import VirtualSource, VirtualLayout
from tomoscan.io import HDF5File
from ..resources.logger import Logger, LoggerOrPrint
from ..io.utils import get_first_hdf5_entry
from .cli_configs import ZSplitConfig
from .utils import parse_params_values

warnings.warn(
    "This command-line utility is intended as a temporary solution. Please do not rely too much on it.",
    Warning
)


def _get_z_translations(fname, entry):
    z_path = path.join(entry, "sample", "z_translation")
    with HDF5File(fname, "r") as fid:
        z_transl = fid[z_path][:]
    return z_transl


class NXZSplitter:
    def __init__(self, fname, output_dir, n_stages=None, entry=None, logger=None, use_virtual_dataset=False):
        self.fname = fname
        self._ext = path.splitext(fname)[-1]
        self.output_dir = output_dir
        self.n_stages = n_stages
        if entry is None:
            entry = get_first_hdf5_entry(fname)
        self.entry = entry
        self.logger = LoggerOrPrint(logger)
        self.use_virtual_dataset = use_virtual_dataset


    def _patch_nx_file(self, fname, mask):
        orig_fname = self.fname
        detector_path = path.join(self.entry, "instrument", "detector")
        sample_path = path.join(self.entry, "sample")
        with HDF5File(fname, "a") as fid:
            def patch_nx_entry(name):
                newval = fid[name][mask]
                del fid[name]
                fid[name] = newval
            detector_entries = [
                path.join(detector_path, what)
                for what in [
                    "count_time", "image_key", "image_key_control"
                ]
            ]
            sample_entries = [
                path.join(sample_path, what)
                for what in [
                    "rotation_angle", "x_translation", "y_translation", "z_translation"
                ]
            ]
            for what in detector_entries + sample_entries:
                self.logger.debug("Patching %s" % what)
                patch_nx_entry(what)
            # Patch "data" using a virtual dataset
            self.logger.debug("Patching data")
            data_path = path.join(detector_path, "data")
            if self.use_virtual_dataset:
                data_shape = fid[data_path].shape
                data_dtype = fid[data_path].dtype
                new_data_shape = (int(mask.sum()), ) + data_shape[1:]
                vlayout = VirtualLayout(
                    shape=new_data_shape, dtype=data_dtype
                )
                vsource = VirtualSource(
                    orig_fname, name=data_path, shape=data_shape, dtype=data_dtype
                )
                vlayout[:] = vsource[mask, :, :]
                del fid[data_path]
                fid[detector_path].create_virtual_dataset("data", vlayout)

        if not(self.use_virtual_dataset):
            data_path = path.join(self.entry, "instrument", "detector", "data")
            with HDF5File(orig_fname, "r") as fid:
                data_arr = fid[data_path][mask, :, :] # Actually load data. Heavy !
            with HDF5File(fname, "a") as fid:
                del fid[data_path]
                fid[data_path] = data_arr


    def z_split(self):
        """
        Split a HDF5-NX file according to different z_translation.
        """
        z_transl = _get_z_translations(self.fname, self.entry)
        different_z = set(z_transl)
        n_z = len(different_z)
        self.logger.info(
            "Detected %d different z values: %s" % (n_z, str(different_z))
        )
        if n_z <= 1:
            raise ValueError("Detected only %d z-value. Stopping." % n_z)
        if self.n_stages is not None and self.n_stages != n_z:
            raise ValueError(
                "Expected %d different stages, but I detected %d"
                % (self.n_stages, n_z)
            )
        masks = [(z_transl == z) for z in different_z]
        for i_z, mask in enumerate(masks):
            fname_curr_z = path.join(
                self.output_dir,
                path.splitext(path.basename(self.fname))[0] + str("_%04d" % i_z) + self._ext
            )
            self.logger.info("Creating %s" % fname_curr_z)
            copy_file(self.fname, fname_curr_z)
            self._patch_nx_file(fname_curr_z, mask)


def zsplit():
    # Parse arguments
    args = parse_params_values(
        ZSplitConfig,
        parser_description="Split a HDF5-Nexus file according to z translation (z-series)"
    )
    # Sanitize arguments
    fname = args["input_file"]
    output_dir = args["output_directory"]
    loglevel = args["loglevel"].upper()
    entry = args["entry"]
    if len(entry) == 0:
        entry = None
    n_stages = args["n_stages"]
    if n_stages < 0:
        n_stages = None
    use_virtual_dataset = bool(args["use_virtual_dataset"])
    # Instantiate and execute
    logger = Logger("NX_z-splitter", level=loglevel, logfile="nxzsplit.log")
    nx_splitter = NXZSplitter(
        fname, output_dir,
        n_stages=n_stages, entry=entry, logger=logger,
        use_virtual_dataset=use_virtual_dataset
    )
    nx_splitter.z_split()


if __name__ == "__main__":
    zsplit()
