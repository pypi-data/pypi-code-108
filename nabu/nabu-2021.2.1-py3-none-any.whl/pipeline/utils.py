from os import path, mkdir
from ..resources.logger import LoggerOrPrint
from ..resources.utils import is_hdf5_extension
from ..utils import check_supported
from ..io.writer import Writers, NXProcessWriter
from ..io.utils import check_h5py_version # won't be necessary once h5py >= 3.0 required
from .params import files_formats
#
# Decorators and callback mechanism
#

def use_options(step_name, step_attr):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if step_name not in self.processing_steps:
                self.__setattr__(step_attr, None)
                return
            self._steps_name2component[step_name] = step_attr
            self._steps_component2name[step_attr] = step_name
            return func(*args, **kwargs)
        return wrapper
    return decorator


def pipeline_step(step_attr, step_desc):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if self.__getattribute__(step_attr) is None:
                return
            self.logger.info(step_desc)
            res = func(*args, **kwargs)
            self.logger.debug("End " + step_desc)
            step_name = self._steps_component2name[step_attr]
            callbacks = self._callbacks.get(step_name, None)
            if callbacks is not None:
                for callback in callbacks:
                    callback(self)
            if step_name in self._data_dump:
                self._dump_data_to_file(step_name)
            return res
        return wrapper
    return decorator


#
# Writer
#

class WriterConfigurator:

    _overwrite_warned = False

    def __init__(
        self, output_dir,
        file_prefix,
        file_format="hdf5",
        overwrite=False,
        start_index=None,
        logger=None,
        nx_info=None,
        write_histogram=False,
        histogram_entry="entry",
        writer_options=None,
        extra_options=None
    ):
        """
        Create a Writer from a set of parameters.

        Parameters
        ----------
        output_dir: str
            Directory where the file(s) will be written.
        file_prefix: str
            File prefix (without leading path)
        start_index: int, optional
            Index to start the files numbering (filename_0123.ext).
            Default is 0.
            Ignored for HDF5 extension.
        logger: nabu.resources.logger.Logger, optional
            Logger object
        nx_info: dict, optional
            Dictionary containing the nexus information.
        write_histogram: bool, optional
            Whether to also write a histogram of data. If set to True, it will configure
            an additional "writer".
        histogram_entry: str, optional
            Name of the HDF5 entry for the output histogram file, if write_histogram is True.
            Ignored if the output format is already HDF5 : in this case, nx_info["entry"] is taken.
        writer_options: dict, optional
            Other advanced options to pass to Writer class.
        """
        self.logger = LoggerOrPrint(logger)
        self.start_index = start_index
        self.write_histogram = write_histogram
        self.overwrite = overwrite
        writer_options = writer_options or {}
        self.extra_options = extra_options or {}

        check_supported(file_format, list(Writers.keys()), "output file format")

        self._set_output_dir(output_dir)
        self._set_file_name(file_prefix, file_format)

        # Init Writer
        writer_cls = Writers[file_format]
        writer_args = [self.fname]
        writer_kwargs = {}
        self._writer_exec_args = []
        self._writer_exec_kwargs = {}
        self._is_hdf5_output = is_hdf5_extension(file_format)

        if self._is_hdf5_output:
            writer_kwargs["entry"] = nx_info["entry"]
            writer_kwargs["filemode"] = "a"
            writer_kwargs["overwrite"] = overwrite
            self._writer_exec_args.append(nx_info["process_name"])
            self._writer_exec_kwargs["processing_index"] = nx_info["processing_index"]
            self._writer_exec_kwargs["config"] = nx_info["config"]
            check_h5py_version(self.logger)
        else:
            writer_kwargs["start_index"] = self.start_index
            if writer_options.get("tiff_single_file", False) and "tif" in file_format:
                do_append = writer_options.get("single_tiff_initialized", False)
                writer_kwargs.update({"multiframe": True, "append": do_append})

        if files_formats.get(file_format, None) == "jp2":
            cratios = self.extra_options.get("jpeg2000_compression_ratio", None)
            if cratios is not None:
                cratios = [cratios]
            writer_kwargs["cratios"] = cratios
            writer_kwargs["float_clip_values"] = self.extra_options.get("float_clip_values", None)
        self.writer = writer_cls(*writer_args, **writer_kwargs)

        if self.write_histogram and not(self._is_hdf5_output):
            self._init_separate_histogram_writer(histogram_entry)


    def _set_output_dir(self, output_dir):
        self.output_dir = output_dir
        if path.exists(self.output_dir):
            if not(path.isdir(self.output_dir)):
                raise ValueError(
                    "Unable to create directory %s: already exists and is not a directory"
                    % self.output_dir
                )
        else:
            self.logger.debug("Creating directory %s" % self.output_dir)
            mkdir(self.output_dir)


    def _set_file_name(self, file_prefix, file_format):
        self.file_prefix = file_prefix
        self.file_format = file_format
        self.fname = path.join(
            self.output_dir,
            file_prefix + "." + file_format
        )
        if path.exists(self.fname):
            err = "File already exists: %s" % self.fname
            if self.overwrite:
                if not(WriterConfigurator._overwrite_warned):
                    self.logger.warning(err + ". It will be overwritten as requested in configuration")
                    WriterConfigurator._overwrite_warned = True
            else:
                self.logger.fatal(err)
                raise ValueError(err)


    def _init_separate_histogram_writer(self, hist_entry):
        hist_fname = path.join(
            self.output_dir,
            "histogram_%04d.hdf5" % self.start_index
        )
        self.histogram_writer = NXProcessWriter(
            hist_fname,
            entry=hist_entry,
            filemode="w",
            overwrite=True,
        )


    def get_histogram_writer(self):
        if not(self.write_histogram):
            return None
        if self._is_hdf5_output:
            return self.writer
        else:
            return self.histogram_writer


    def write_data(self, data):
        self.writer.write(
            data,
            *self._writer_exec_args,
            **self._writer_exec_kwargs
        )
