from os import path
import posixpath
import numpy as np
from ...preproc.ctf import CTFPhaseRetrieval, GeoPars
from ...resources.logger import LoggerOrPrint
from ...utils import recursive_copy_dict, ArrayPlaceHolder
from ...io.reader import ChunkReader, HDF5Loader, load_images_stack_from_hdf5, get_hdf5_dataset_shape
from ...io.utils import get_first_hdf5_entry
from ..utils import use_options, pipeline_step, WriterConfigurator
from .chunked import ChunkedPipeline


# TODO for now this class inherits from ChunkedPipeline, although its principle is quite different.
# But many methods can be re-used from ChunkedPipeline.
# Create a base class ?
class GroupedPipeline(ChunkedPipeline):
    """
    A class for processig groups of radios.
    """
    backend = "numpy"

    def __init__(self, process_config, images_group, sub_region=None, logger=None, extra_options=None):
        """
        Initialize a GroupedPipeline object.

        Parameters
        ----------
        process_config: ProcessConfig
            Pipeline description.
        images_group: tuple of two int
            Images group to process, in the form (start, end) where end-start == group_size.
            The "end" index is not included, as in standard Python indexing.
            This parameter can be reset while calling process_group(), in order to process another group of images.
        sub_region: tuple, optional
            sub-region to consider for each image, in the form `(start_x, end_x)` or `(start_x, end_x, start_z, end_z)`.
            If provided, each image will be cropped as `image[:, start_x:end_x]` or `image[start_z:end_z, start_x:end_x]`
        logger: Logger, optional
            logging object. If not provided, a new logging object is created.
        extra_options: dict, optional
            dict of advanced options. See "Other Parameters" for these options.


        Other parameters
        ----------------
        Advanced parameters can be passed through the "extra_options" dict.
        Current options are: None


        Important
        ----------
        This class is to be used when you want to process images by groups, not by chunks.
        Contrarily to `ChunkedPipeline`, the sub_region (start_x, end_x, start_z, end_z) cannot be changed.
        What can be changed is only the "images group".
        In short:

           - Use `ChunkedPipeline` to process `images[:, 0:100, :]` then `images[:, 100:200, :]`, etc
           - Use `GroupedPipeline` to process `images[0:1000, :, :]` then `images[1000:2000, :, :]`, etc

        """
        self.logger = LoggerOrPrint(logger)
        self._set_params(process_config, images_group, sub_region, extra_options)
        self._init_pipeline()


    def _set_params(self, process_config, images_group, sub_region, extra_options):
        self.process_config = process_config
        self._phase_margin = None
        self.dataset_info = self.process_config.dataset_info
        self.dataset_infos = self.process_config.dataset_info # other shorthand - deprecated
        self.processing_steps = self.process_config.processing_steps.copy()
        self._orig_processing_options = recursive_copy_dict(self.process_config.processing_options)
        self.processing_options = recursive_copy_dict(self.process_config.processing_options)

        self._set_group(images_group)
        self._set_subregion(sub_region)
        self._set_extra_options(extra_options)
        self._callbacks = {}
        self._orig_file_prefix = None
        self._steps_name2component = {}
        self._steps_component2name = {}
        self._data_dump = {}
        self._phase_margin_up = 0 # Compat.
        self._resume_from_step = None


    def _set_group(self, images_group):
        self.images_group = images_group
        self.group_size = images_group[1] - images_group[0]


    def _set_subregion(self, sub_region):
        if sub_region is None:
            sub_region = (None, None, None, None)
        if len(sub_region) == 4:
            start_x, end_x, start_z, end_z = sub_region
        elif len(sub_region) == 2:
            first_part, second_part = sub_region
            if np.iterable(first_part): # ((sx, ex), (sz, ez))
                start_x, end_x = first_part
                start_z, end_z = second_part
            else: # (sx, ex, sz, ez)
                start_x, end_x = first_part, second_part
                start_z, end_z = None, None
        self.sub_region = (start_x, end_x, start_z, end_z)
        self.z_min = start_z or 0


    def _get_phase_margin(self):
        return ((0, 0), (0, 0))


    def _get_shape(self, step_name):
        radios_3D_shape = self.radios.shape
        radio_2D_shape = radios_3D_shape[1:]
        shapes = {
            "flatfield": radios_3D_shape,
            "double_flatfield": radios_3D_shape,
            "ccd_correction": radio_2D_shape,
            "phase": radio_2D_shape,
            "unsharp_mask": radio_2D_shape,
            "take_log": radios_3D_shape,
            "radios_movements": radios_3D_shape,
            "rotate_projections": radio_2D_shape,
        }
        if step_name not in shapes:
            raise ValueError("Cannot figure out shape for step '%s'" % step_name)
        shape = shapes[step_name]
        self.logger.debug("Data shape for %s is %s" % (step_name, str(shape)))
        return shape


    def _check_resume_from_step(self):
        if self._resume_from_step is None:
            return
        expected_radios_shape = get_hdf5_dataset_shape(
            self.processing_options["read_chunk"]["process_file"],
            self.processing_options["read_chunk"]["process_h5_path"],
            sub_region=(self.images_group[0], self.images_group[1], None, None, None, None) # (n_angles, n_z, n_x)
        )
        if expected_radios_shape[0] != self.images_group[1] - self.images_group[0]:
            msg = "Expected to find data with n_angles>=%d in %s but found n_angles=%d" % (
                self.images_group[1] - self.images_group[0],
                self.processing_options["read_chunk"]["process_file"],
                expected_radios_shape[0]
            )
            self.logger.fatal(msg)
            raise ValueError(msg)
        if expected_radios_shape[1] != self.dataset_info.radio_dims[1]:
            msg = "Expected to find data with n_y=%d in %s but found n_y=%d" % (
                self.dataset_info.radio_dims[1],
                self.processing_options["read_chunk"]["process_file"],
                expected_radios_shape[1]
            )
            self.logger.fatal(msg)
            raise ValueError(msg)


    def _init_reader_finalize(self):
        """
        Method called after _init_reader
        """
        self._check_resume_from_step()
        self.radios = self.chunk_reader.data
        self._radios_cropped = self.radios # compat. with ChunkedPipeline

    def _error_na(self):
        raise ValueError("This function is not applicable with the current class")


    def _do_nothing(self):
        pass

    _reset_sub_region = _error_na
    process_chunk = _error_na
    _process_chunk = _error_na
    _write_histogram = _do_nothing


    #
    # Pipeline initialization
    #

    def _init_pipeline(self):
        self._init_reader()
        self._init_flatfield()
        self._init_double_flatfield()
        self._init_ccd_corrections()
        self._init_radios_rotation()
        self._init_phase()
        self._init_unsharp()
        self._init_mlog()
        self._init_radios_movements()
        self._init_writer()
        self._configure_data_dumps()


    def _update_reader_configuration(self):
        """
        Modify self.processing_options["read_chunk"] to select a subset of the files
        """
        options = self.processing_options["read_chunk"]
        self._resume_from_step = options.get("step_name", None)
        if self._resume_from_step is not None:
            if self._resume_from_step == "sinogram":
                msg = "It makes no sense to use this class when resuming process from sinogram"
                self.logger.fatal(msg)
                raise ValueError(msg)
            return
        orig_options = self._orig_processing_options["read_chunk"]
        input_data_files = {}
        files_indices = sorted(orig_options["files"].keys())
        for i in range(self.images_group[0], self.images_group[1]):
            idx = files_indices[i]
            input_data_files[idx] = orig_options["files"][idx]
        options["files"] = input_data_files

    def _get_image_start_index(self):
        return self.images_group[0]

    @use_options("read_chunk", "chunk_reader")
    def _init_reader(self):
        if "read_chunk" not in self.processing_steps:
            raise ValueError("Cannot proceed without reading data")
        options = self.processing_options["read_chunk"]

        self._update_reader_configuration()

        if self._resume_from_step is None:
            # Standard case - start pipeline from raw data
            self.chunk_reader = ChunkReader(
                options["files"],
                sub_region=self.sub_region,
                convert_float=True,
                binning=options["binning"],
                dataset_subsampling=options["dataset_subsampling"]
            )
        else:
            # Resume pipeline from dumped intermediate step
            self.chunk_reader = HDF5Loader(
                options["process_file"],
                options["process_h5_path"],
                sub_region=(self.images_group[0], self.images_group[1], None, None, None, None),
                pre_allocate=True,
            )
        self._init_reader_finalize()


    def _update_flatfield_configuration(self):
        """
        Modify self.processing_options["flatfield"] to select a subset of the files
        """
        options = self.processing_options.get("flatfield", None)
        if options is None:
            return
        # ChunkReader.files accounts for subsampling
        options["projs_indices"] = sorted(self.chunk_reader.files_subsampled.keys())


    def _init_flatfield(self, shape=None):
        self._update_flatfield_configuration()
        ChunkedPipeline._init_flatfield(self, shape=shape)


    def _init_ctf_phase(self):
        options = self.processing_options["phase"]

        geo_pars_params = options["ctf_geo_pars"].copy()
        geo_pars_params["logger"] = self.logger
        geo_pars = GeoPars(**geo_pars_params)

        self.phase_retrieval = CTFPhaseRetrieval(
            geo_pars, options["delta_beta"],
            lim1=options["ctf_lim1"], lim2=options["ctf_lim2"],
            logger=self.logger
        )


    @use_options("phase", "phase_retrieval")
    def _init_phase(self):
        options = self.processing_options["phase"]
        if options["method"] == "CTF":
            self._init_ctf_phase()
        else:
            super()._init_phase()


    @use_options("save", "writer")
    def _init_writer(self):
        options = self.processing_options["save"]
        file_prefix = options["file_prefix"]
        output_dir = path.join(
            options["location"],
            file_prefix
        )
        file_prefix = "sinogram_" + file_prefix + str(
            "_%04d" % self.images_group[0]
        )
        entry = getattr(self.dataset_info.dataset_scanner, "entry", None)
        nx_info = {
            "process_name": "sinogram",
            "processing_index": 0,
            "config": {
                # "processing_options": self.processing_options, # Takes too much time to write, not useful for partial files
                "nabu_config": self.process_config.nabu_config
            },
            "entry": entry,
        }
        self._writer_configurator = WriterConfigurator(
            output_dir, file_prefix,
            file_format="hdf5",
            overwrite=options["overwrite"],
            start_index=self.images_group[0],
            logger=self.logger,
            nx_info=nx_info,
            write_histogram=False
        )
        self.writer = self._writer_configurator.writer
        self.histogram_writer = None
        self._writer_exec_args = self._writer_configurator._writer_exec_args
        self._writer_exec_kwargs = self._writer_configurator._writer_exec_kwargs


    def _get_cropped_radios(self):
        return self.radios


    def _configure_data_dumps(self):
        super()._configure_data_dumps()
        # dumping sinogram is natively done by this class.
        self._data_dump.pop("sinogram", None)


    #
    # Pipeline re-initialization
    #

    def _reset_images_group(self, images_group):
        if images_group[1] - images_group[0] != self.group_size:
            raise ValueError(
                "This class was instantiated with group_size=%d, but images_group=%s was passed"
                % (self.group_size, str(images_group))
            )
        self._set_group(images_group)
        # Reader
        self._update_reader_configuration()
        if self._resume_from_step is None:
            self.chunk_reader._set_files(self.processing_options["read_chunk"]["files"])
            self.chunk_reader._loaded = False
        else:
            self.chunk_reader._set_subregion((self.images_group[0], self.images_group[1], None, None, None, None))
            self.chunk_reader._loaded = False
        # Flat-field
        self._reset_flatfield()

    def _reset_flatfield(self):
        if self.flatfield is None:
            return
        new_radios_indices = self.processing_options["flatfield"]["projs_indices"]
        self.flatfield.radios_indices = np.array(new_radios_indices, dtype=np.int32)


    #
    # Pipeline execution
    #

    @pipeline_step("phase_retrieval", "Performing phase retrieval")
    def _retrieve_phase_ctf(self):
        options = self.processing_options["phase"]
        padding_mode = options["padding_type"]
        for i in range(self.radios.shape[0]):
            self.radios[i] = self.phase_retrieval.retrieve_phase(
                self.radios[i],
                padding_mode=padding_mode,
                # translation_vh=self.dataset_info.ctf_translations[i], # TODO unsupported
                translation_vh=None,
                normalize_by_mean=options["ctf_normalize_by_mean"],
            )


    def _retrieve_phase(self):
        if "phase" not in self.processing_steps:
            return
        options = self.processing_options["phase"]
        if options["method"] == "CTF":
            self._retrieve_phase_ctf()
        else:
            super()._retrieve_phase()


    def _process_group(self):
        self._flatfield()
        self._double_flatfield()
        self._ccd_corrections()
        self._retrieve_phase()
        self._apply_unsharp()
        self._take_log()
        self._rotate_projections()
        self._radios_movements()
        self._write_data(data=self.radios)


    def process_group(self, images_group=None):
        if images_group is not None:
            self._reset_images_group(images_group)
            self._reset_memory()
            self._init_writer()
            self._init_double_flatfield()
            self._configure_data_dumps()
        self._read_data()
        self._process_group()


class SinoStackPipeline:
    backend = "numpy"
    SinoNormalizationClass = ChunkedPipeline.SinoNormalizationClass
    SinoBuilderClass = ChunkedPipeline.SinoBuilderClass
    SinoDeringerClass = ChunkedPipeline.SinoDeringerClass
    FBPClass = ChunkedPipeline.FBPClass
    HistogramClass = ChunkedPipeline.HistogramClass


    """
    A pipeline for processing tomography data from sinograms.
    This class is to be used to complement GroupedPipeline.
    """
    def __init__(self, process_config, stack, projections, logger=None, extra_options=None):
        """
        Initialize a SinoStackPipeline.

        Parameters
        ----------
        process_config: ProcessConfig object
            Data structure with the processing configuration
        stack: tuple
            Tuple in the form (start_z, end_z)
        projections: str or array
           Pre-processed projections. Sinogram will be directly built from these projections.
           This parameter can of be the following type:

              - str: path to the HDF5 (master) file containing the projections (radios).
              - array: an array already containing the projections.


        Other parameters
        ----------------
        logger: Logger, optional
            Logging object
        extra_options: dict, optional
            Dictionary with extra options.
        """
        self.logger = LoggerOrPrint(logger)
        self._set_params(process_config, projections, stack, extra_options)
        self._init_pipeline()


    def _set_params(self, process_config, projections, stack, extra_options):
        self._set_extra_options(extra_options)
        self.process_config = process_config
        self.processing_steps = process_config.processing_steps
        self.processing_options = process_config.processing_options
        self.dataset_info = process_config.dataset_info
        self.projections = projections
        self._set_stack(stack)
        self._steps_name2component = {}
        self._steps_component2name = {}
        self._callbacks = {}
        self.use_radio_processing_margin = False
        self.chunk_reader = "get_projections"
        self._data_dump = {}


    def _set_stack(self, stack):
        if len(stack) != 2:
            raise ValueError("Expected 2-tuple (z_min, z_max)")
        self.z_min, self.z_max = stack
        self.images_stack = stack
        self.stack = stack


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {
            "projections_processing_name": "sinogram",
        }
        advanced_options.update(extra_options)
        self.extra_options = advanced_options


    def _get_shape(self, step_name):
        radios_3D_shape = self.radios.shape
        radio_2D_shape = radios_3D_shape[1:]
        if step_name == "sino_normalization":
            shape = radios_3D_shape
        elif step_name == "build_sino":
            shape = radios_3D_shape
        elif step_name == "sino_rings_correction":
            shape = self.sino_builder.output_shape
        elif step_name == "reconstruction":
            shape = self.sino_builder.output_shape[1:]
        else:
            raise ValueError("Cannot figure out shape for step '%s'" % step_name)
        self.logger.debug("Data shape for %s is %s" % (step_name, str(shape)))
        return shape

    #
    # Pipeline initialization
    #
    @use_options("read_chunk", "chunk_reader")
    def _init_reader(self):
        if isinstance(self.projections, str):
            fname = self.projections
            h5_entry = self.process_config.nabu_config["dataset"]["hdf5_entry"] or get_first_hdf5_entry(fname)
            self._data_h5_path = posixpath.join(
                h5_entry,
                self.extra_options["projections_processing_name"], "results", "data"
            )
            self.data_reader = HDF5Loader(
                fname,
                self._data_h5_path,
                sub_region=(None, None, self.stack[0], self.stack[1], None, None)
            )
            self.radios = self.data_reader.data
        elif isinstance(self.projections, np.ndarray):
            self.radios = self.projections
        else:
            raise ValueError("Expected str, list or array for 'projections'")


    def _get_slice_start_index(self):
        return self.z_min


    _allocate_array = ChunkedPipeline._allocate_array
    _allocate_sinobuilder_output = ChunkedPipeline._allocate_sinobuilder_output
    _prepare_reconstruction = ChunkedPipeline._prepare_reconstruction
    _allocate_recs = ChunkedPipeline._allocate_recs
    _init_sino_normalization = ChunkedPipeline._init_sino_normalization
    _init_sino_builder = ChunkedPipeline._init_sino_builder
    _init_sino_rings_correction = ChunkedPipeline._init_sino_rings_correction
    _init_histogram = ChunkedPipeline._init_histogram
    _init_writer = ChunkedPipeline._init_writer


    def _init_pipeline(self):
        self._init_reader()
        self._init_sino_normalization()
        self._init_sino_builder()
        self._init_sino_rings_correction()
        self._prepare_reconstruction()
        self._init_reconstruction()
        self._init_histogram()
        self._init_writer()


    #
    # Pipeline execution
    #

    @pipeline_step("chunk_reader", "Reading data")
    def _read_data(self):
        if isinstance(self.projections, str):
            self.data_reader.load_data()


    _normalize_sinos = ChunkedPipeline._normalize_sinos
    _build_sino = ChunkedPipeline._build_sino
    _destripe_sinos = ChunkedPipeline._destripe_sinos
    _init_reconstruction = ChunkedPipeline._init_reconstruction
    _reconstruct = ChunkedPipeline._reconstruct
    _compute_histogram = ChunkedPipeline._compute_histogram
    _write_data = ChunkedPipeline._write_data
    _write_histogram = ChunkedPipeline._write_histogram
    _get_process_name = ChunkedPipeline._get_process_name


    def _reset_stack(self, stack):
        self._set_stack(stack)
        self._init_reader()
        self._init_writer()


    def _process_stack(self):
        self._normalize_sinos()
        self._build_sino()
        self._destripe_sinos()
        self._reconstruct()
        self._compute_histogram()
        self._write_data()


    def process_stack(self, stack=None):
        if stack is not None:
            self._reset_stack(stack)
        self._read_data()
        self._process_stack()
