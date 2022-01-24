from glob import glob
from os import path, getcwd, chdir
from posixpath import join as posix_join
from datetime import datetime
from packaging.version import parse as parse_version
import numpy as np
from h5py import VirtualSource, VirtualLayout
from tomoscan.io import HDF5File
from silx.io.dictdump import dicttoh5
from tifffile import TiffWriter
from .. import version as nabu_version
from ..utils import merged_shape, deprecation_warning, get_available_threads
from ..misc.utils import rescale_data
from .utils import check_h5py_version, convert_dict_values
try:
    from silx.third_party.EdfFile import EdfFile
except ImportError:
    EdfFile = None
try:
    from glymur import Jp2k, set_option as glymur_set_option
    from glymur.version import openjpeg_version, version as glymur_version
    __have_jp2k__ = True
except ImportError:
    __have_jp2k__ = False

def get_datetime():
    """
    Function used by some writers to indicate the current date.
    """
    return datetime.now().replace(microsecond=0).isoformat()


class Writer:
    """
    Base class for all writers.
    """
    def __init__(self, fname):
        self.fname = fname


    def get_filename(self):
        return self.fname



def h5_write_object(h5group, key, value, overwrite=False, default_val=None):
    existing_val = h5group.get(key, default_val)
    if existing_val is not default_val:
        if not overwrite:
            raise OSError("Unable to create link (name already exists): %s" % h5group.name)
        else:
            h5group.pop(key)
    h5group[key] = value


class NXProcessWriter(Writer):
    """
    A class to write Nexus file with a processing result.
    """
    def __init__(self, fname, entry=None, filemode="a", overwrite=False):
        """
        Initialize a NXProcessWriter.

        Parameters
        -----------
        fname: str
            Path to the HDF5 file.
        entry: str, optional
            Entry in the HDF5 file. Default is "entry"
        """
        super().__init__(fname)
        self._set_entry(entry)
        self._filemode = filemode
        self.overwrite = overwrite
        check_h5py_version()


    def _set_entry(self, entry):
        self.entry = entry or "entry"
        data_path = posix_join("/", self.entry)
        self.data_path = data_path


    def write(self, result, process_name, processing_index=0, config=None, data_name="data", is_frames_stack=True):
        """
        Write the result in the current NXProcess group.

        Parameters
        ----------
        result: numpy.ndarray
            Array containing the processing result
        process_name: str
            Name of the processing
        processing_index: int
            Index of the processing (in a pipeline)
        config: dict, optional
            Dictionary containing the configuration.
        """
        swmr = (self._filemode == "r")
        with HDF5File(self.fname, self._filemode, swmr=swmr) as fid:
            nx_entry = fid.require_group(self.data_path)
            if "NX_class" not in nx_entry.attrs:
                nx_entry.attrs["NX_class"] = "NXentry"

            nx_process = nx_entry.require_group(process_name)
            nx_process.attrs['NX_class'] = "NXprocess"

            metadata = {
                "program": "nabu",
                "version": nabu_version,
                "date": get_datetime(),
                "sequence_index": np.int32(processing_index),
            }
            for key, val in metadata.items():
                h5_write_object(nx_process, key, val, overwrite=self.overwrite)

            if config is not None:
                export_dict_to_h5(
                    config,
                    self.fname,
                    posix_join(nx_process.name, "configuration"),
                    overwrite_data=True,
                    mode="a"
                )
                nx_process['configuration'].attrs['NX_class'] = "NXcollection"
            if isinstance(result, dict):
                results_path = posix_join(nx_process.name, "results")
                export_dict_to_h5(
                    result,
                    self.fname,
                    results_path,
                    overwrite_data=self.overwrite,
                    mode="a"
                )
            else:
                nx_data = nx_process.require_group('results')
                results_path = nx_data.name
                nx_data.attrs['NX_class'] = "NXdata"
                nx_data.attrs['signal'] = data_name

                results_data_path = posix_join(results_path, data_name)
                if self.overwrite and results_data_path in fid:
                    del fid[results_data_path]

                if isinstance(result, VirtualLayout):
                    nx_data.create_virtual_dataset(data_name, result)
                else: # assuming array-like
                    nx_data[data_name] = result
                if is_frames_stack:
                    nx_data[data_name].attrs['interpretation'] = "image"
                nx_data.attrs["signal"] = data_name

            # prepare the direct access plots
            nx_process.attrs['default'] = 'results'
            if "default" not in nx_entry.attrs:
                nx_entry.attrs["default"] = posix_join(nx_process.name, 'results')
            # Return the internal path to "results"
            return results_path



def create_virtual_layout(files_or_pattern, h5_path, base_dir=None, axis=0):
    """
    Create a HDF5 virtual layout.

    Parameters
    ----------
    files_or_pattern: str or list
        A list of file names, or a wildcard pattern.
        If a list is provided, it will not be sorted! This will have to be
        done before calling this function.
    h5_path: str
        Path inside the HDF5 input file(s)
    base_dir: str, optional
        Base directory when using relative file names.
    axis: int, optional
        Data axis to merge. Default is 0.
    """
    prev_cwd = None
    if base_dir is not None:
        prev_cwd = getcwd()
        chdir(base_dir)
    if isinstance(files_or_pattern, str):
        files_list = glob(files_or_pattern)
        files_list.sort()
    else: # list
        files_list = files_or_pattern
    if files_list == []:
        raise ValueError("Nothing found as pattern %s" % files_or_pattern)
    virtual_sources = []
    shapes = []
    for fname in files_list:
        with HDF5File(fname, "r", swmr=True) as fid:
            shape = fid[h5_path].shape
        vsource = VirtualSource(fname, name=h5_path, shape=shape)
        virtual_sources.append(vsource)
        shapes.append(shape)
    total_shape = merged_shape(shapes, axis=axis)
    n_images = total_shape[axis]

    virtual_layout = VirtualLayout(
        shape=total_shape,
        dtype='f'
    )
    start_idx = 0
    for vsource, shape in zip(virtual_sources, shapes):
        n_imgs = shape[axis]
        # Perhaps there is more elegant
        if axis == 0:
            virtual_layout[start_idx:start_idx + n_imgs] = vsource
        elif axis == 1:
            virtual_layout[:, start_idx:start_idx + n_imgs, :] = vsource
        elif axis == 2:
            virtual_layout[:, :, start_idx:start_idx + n_imgs] = vsource
        else:
            raise ValueError("Only axis 0,1,2 are supported")
        #
        start_idx += n_imgs

    if base_dir is not None:
        chdir(prev_cwd)
    return virtual_layout



def merge_hdf5_files(
    files_or_pattern, h5_path, output_file, process_name,
    output_entry=None, output_filemode="a", data_name="data",
    processing_index=0, config=None, base_dir=None,
    axis=0, overwrite=False
):
    """
    Parameters
    -----------
    files_or_pattern: str or list
        A list of file names, or a wildcard pattern.
        If a list is provided, it will not be sorted! This will have to be
        done before calling this function.
    h5_path: str
        Path inside the HDF5 input file(s)
    output_file: str
        Path of the output file
    process_name: str
        Name of the process
    output_entry: str, optional
        Output HDF5 root entry (default is "/entry")
    output_filemode: str, optional
        File mode for output file. Default is "a" (append)
    processing_index: int, optional
        Processing index for the output file. Default is 0.
    config: dict, optional
        Dictionary describing the configuration needed to get the results.
    base_dir: str, optional
        Base directory when using relative file names.
    axis: int, optional
        Data axis to merge. Default is 0.
    overwrite: bool, optional
        Whether to overwrite already existing data in the final file.
        Default is False.
    """
    if base_dir is not None:
        prev_cwd = getcwd()
    virtual_layout = create_virtual_layout(files_or_pattern, h5_path, base_dir=base_dir, axis=axis)
    nx_file = NXProcessWriter(
        output_file,
        entry=output_entry, filemode=output_filemode, overwrite=overwrite
    )
    nx_file.write(
        virtual_layout,
        process_name,
        processing_index=processing_index,
        config=config,
        data_name=data_name,
        is_frames_stack=True
    )
    if base_dir is not None and prev_cwd != getcwd():
        chdir(prev_cwd)


class TIFFWriter(Writer):
    def __init__(self, fname, multiframe=False, start_index=0, filemode=None, append=False, big_tiff=None):
        """
        Tiff writer.

        Parameters
        -----------
        fname: str
            Path to the output file name
        multiframe: bool, optional
            Whether to write all data in one single file. Default is False.
        start_index: int, optional
            When writing a stack of images, each image is written in a dedicated file
            (unless multiframe is set to True).
            In this case, the output is a series of files `filename_0000.tif`,
            `filename_0001.tif`, etc. This parameter is the starting index for
            file names.
            This option is ignored when multiframe is True.
        filemode: str, optional
            DEPRECATED. Will be ignored. Please refer to 'append'
        append: bool, optional
            Whether to append data to the file rather than overwriting. Default is False.
        big_tiff: bool, optional
            Whether to write in "big tiff" format: https://www.awaresystems.be/imaging/tiff/bigtiff.html
            Default is True when multiframe is True.
            Note that default "standard" tiff cannot exceed 4 GB.

        Notes
        ------
        If multiframe is False (default), then each image will be written in a
        dedicated tiff file.
        """
        super().__init__(fname)
        self.multiframe = multiframe
        self.start_index = start_index
        self.append = append
        if big_tiff is None:
            big_tiff = multiframe
        if multiframe and not big_tiff:
            # raise error ?
            print("big_tiff was set to False while multiframe was set to True. This will probably be problematic.")
        self.big_tiff = big_tiff
        # Compat.
        self.filemode = filemode
        if filemode is not None:
            deprecation_warning("Ignored parameter 'filemode'. Please use the 'append' parameter")
        #

    def _write_tiff(self, data, config=None, filename=None):
        # TODO metadata
        filename = filename or self.fname
        with TiffWriter(filename, bigtiff=self.big_tiff, append=self.append) as tif:
            tif.write(data)

    def write(self, data, *args, config=None, **kwargs):
        # Single image, or multiple image in the same file
        if self.multiframe or data.ndim < 3 or ((data.ndim == 3) and (data.shape[0] == 1)):
            self._write_tiff(data, config=config)
        # Multiple image, one file per image
        else:
            dirname, rel_filename = path.split(self.fname)
            prefix, ext = path.splitext(rel_filename)
            for i in range(data.shape[0]):
                curr_rel_filename = prefix + str("_%04d" % (self.start_index + i)) + ext
                fname = path.join(dirname, curr_rel_filename)
                self._write_tiff(data[i], filename=fname, config=config)

    def get_filename(self):
        if self.multiframe:
            return self.fname
        else:
            return path.dirname(self.fname)


class EDFWriter(Writer):
    def __init__(self, fname, start_index=0, filemode="w"):
        """
        EDF (ESRF Data Format) writer.

        Parameters
        -----------
        fname: str
            Path to the output file name
        start_index: int, optional
            When writing a stack of images, each image is written in a dedicated file
            In this case, the output is a series of files `filename_0000.tif`,
            `filename_0001.edf`, etc. This parameter is the starting index for
            file names.
        """
        super().__init__(fname)
        self.filemode = filemode
        self.start_index = start_index

    def _write_edf(self, data, config=None, filename=None, filemode=None):
        if filename is None:
            filename = self.fname
        edf = EdfFile(filename, access="w+b")
        config = config or {}
        config["software"] = str("nabu %s" % nabu_version)
        config["date"] = get_datetime()
        edf.WriteImage(
            config,
            data
        )
        edf = None


    def write(self, data, *args, config=None, **kwargs):
        if data.ndim < 3:
            self._write_edf(data, config=config)
            return
        if (data.ndim == 3) and (data.shape[0] == 1):
            self._write_edf(data[0], config=config)
            return
        dirname, rel_filename = path.split(self.fname)
        prefix, ext = path.splitext(rel_filename)
        for i in range(data.shape[0]):
            curr_rel_filename = prefix + str("_%04d" % (self.start_index + i)) + ext
            fname = path.join(dirname, curr_rel_filename)
            self._write_edf(data[i], filename=fname, config=config)

    def get_filename(self):
        return path.dirname(self.fname)


class JP2Writer(Writer):
    def __init__(
        self, fname, start_index=0, filemode="wb",
        psnr=None, cratios=None, auto_convert=True, float_clip_values=None, n_threads=None
    ):
        """
        JPEG2000 writer. This class requires the python package `glymur` and the
        library `libopenjp2`.

        Parameters
        -----------
        fname: str
            Path to the output file name
        start_index: int, optional
            When writing a stack of images, each image is written in a dedicated file
            The output is a series of files `filename_0000.tif`, `filename_0001.tif`, etc.
            This parameter is the starting index for file names.
        psnr: list of int, optional
            The PSNR (Peak Signal-to-Noise ratio) for each jpeg2000 layer.
            This defines a quality metric for lossy compression.
            The number "0" stands for lossless compression.
        cratios: list of int, optional
            Compression ratio for each jpeg2000 layer
        auto_convert: bool, optional
            Whether to automatically cast floating point data to uint16.
            Default is True.
        float_clip_values: tuple of floats, optional
            If set to a tuple of two values (min, max), then each image values will be clipped
            to these minimum and maximum values.
        n_threads: int, optional
            Number of threads to use for encoding. Default is the number of available threads.
            Needs libopenjpeg >= 2.4.0.
        """
        super().__init__(fname)
        if not(__have_jp2k__):
            raise ValueError("Need glymur python package and libopenjp2 library")
        self.setup_multithread_encoding(n_threads=n_threads, what_if_not_available="ignore")
        self.filemode = filemode
        self.start_index = start_index
        self.auto_convert = auto_convert
        if psnr is not None and np.isscalar(psnr):
            psnr = [psnr]
        self.psnr = psnr
        self.cratios = cratios
        self._vmin = None
        self._vmax = None
        self.clip_float = False
        if float_clip_values is not None:
            self._float_clip_min, self._float_clip_max = float_clip_values
            self.clip_float = True


    @staticmethod
    def setup_multithread_encoding(n_threads=None, what_if_not_available="ignore"):
        """
        Setup OpenJpeg multi-threaded encoding.

        Parameters
        -----------
        n_threads: int, optional
            Number of threads. If not provided, all available threads are used.
        na: str, optional
            What to do if requirements are not fulfilled. Possible values are:
               - "ignore": do nothing, proceed
               - "print": show an information message
               - "raise": raise an error
        """
        required_glymur_version = "0.9.3"
        required_openjpeg_version = "2.4.0"

        def not_available(msg):
            if what_if_not_available == "raise":
                raise ValueError(msg)
            elif what_if_not_available == "print":
                print(msg)

        requirements = [
            ("glymur", glymur_version, required_glymur_version),
            ("libopenjpeg", openjpeg_version, required_openjpeg_version)
        ]
        for what, current_version, required_version in requirements:
            if parse_version(current_version) < parse_version(required_version):
                not_available(
                    "%s version >= %s is required for multi-threaded encoding (current version: %s)"
                    % (what, required_version, current_version)
                )
                return
        if n_threads is None:
            n_threads = get_available_threads()
        glymur_set_option("lib.num_threads", n_threads)


    def _write_jp2k(self, data, filename=None):
        if filename is None:
            filename = self.fname
        if data.dtype != np.uint16 and self.auto_convert:
            if self.clip_float:
                data = np.clip(data, self._float_clip_min, self._float_clip_max)
            data = rescale_data(data, 0, 65535, data_min=self._vmin, data_max=self._vmax)
            data = data.astype(np.uint16)
        #
        jp2 = Jp2k(filename, data=data, psnr=self.psnr, cratios=self.cratios)


    def write(self, data, *args, **kwargs):
        if data.ndim < 3:
            self._write_jp2k(data)
            return
        if (data.ndim == 3) and (data.shape[0] == 1):
            self._write_jp2k(data[0])
            return
        dirname, rel_filename = path.split(self.fname)
        prefix, ext = path.splitext(rel_filename)
        for i in range(data.shape[0]):
            curr_rel_filename = prefix + str("_%04d" % (self.start_index + i)) + ext
            fname = path.join(dirname, curr_rel_filename)
            self._write_jp2k(data[i], filename=fname)


    def get_filename(self):
        return path.dirname(self.fname)


class NPYWriter(Writer):
    def __init__(self,  fname):
        super().__init__(fname)

    def write(self, result, *args, **kwargs):
        np.save(self.fname, result)


class NPZWriter(Writer):
    def __init__(self,  fname):
        super().__init__(fname)

    def write(self, result, *args, **kwargs):
        save_args = {"result": result}
        config = kwargs.get("config", None)
        if config is not None:
            save_args["configuration"] = config
        np.savez(self.fname, **save_args)


Writers = {
    "h5": NXProcessWriter,
    "hdf5": NXProcessWriter,
    "nx": NXProcessWriter,
    "nexus": NXProcessWriter,
    "npy": NPYWriter,
    "npz": NPZWriter,
    "tif": TIFFWriter,
    "tiff": TIFFWriter,
    "j2k": JP2Writer,
    "jp2": JP2Writer,
    "jp2k": JP2Writer,
    "edf": EDFWriter,
}


def export_dict_to_h5(dic, h5file, h5path, overwrite_data=True, mode="a"):
    """
    Wrapper on top of silx.io.dictdump.dicttoh5 replacing None with "None"

    Parameters
    -----------
    dic: dict
        Dictionary containing the options
    h5file: str
        File name
    h5path: str
        Path in the HDF5 file
    overwrite_data: bool, optional
        Whether to overwrite data when writing HDF5. Default is True
    mode: str, optional
        File mode. Default is "a" (append).
    """
    modified_dic = convert_dict_values(
        dic,
        {None: "None"},
    )
    update_mode = {True: 'modify', False: 'add'}[bool(overwrite_data)]
    return dicttoh5(
        modified_dic,
        h5file=h5file,
        h5path=h5path,
        update_mode=update_mode,
        mode=mode
    )