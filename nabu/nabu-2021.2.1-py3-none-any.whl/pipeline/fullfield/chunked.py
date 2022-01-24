from os import path
from time import time
import numpy as np
from silx.io.url import DataUrl
from ...resources.logger import LoggerOrPrint
from ...resources.utils import is_hdf5_extension, extract_parameters
from ...io.reader import ChunkReader, HDF5Loader, get_hdf5_dataset_shape
from ...preproc.ccd import Log, CCDFilter
from ...preproc.flatfield import FlatFieldDataUrls
from ...preproc.distortion import DistortionCorrection
from ...preproc.shift import VerticalShift
from ...preproc.double_flatfield import DoubleFlatField
from ...preproc.phase import PaganinPhaseRetrieval
from ...reconstruction.sinogram import SinoBuilder, SinoNormalization
from ...misc.rotation import Rotation
from ...preproc.rings import MunchDeringer
from ...misc.unsharp import UnsharpMask
from ...misc.histogram import PartialHistogram, hist_as_2Darray
from ..utils import use_options, pipeline_step, WriterConfigurator
# For now we don't have a plain python/numpy backend for reconstruction
try:
    from ...reconstruction.fbp_opencl import Backprojector
except:
    Backprojector = None


class ChunkedPipeline:
    """
    Pipeline for "regular" full-field tomography.
    Data is processed by chunks. A chunk consists in K contiguous lines of all the radios.
    In parallel geometry, a chunk of K radios lines gives K sinograms,
    and equivalently K reconstructed slices.
    """

    backend = "numpy"
    FlatFieldClass = FlatFieldDataUrls
    DoubleFlatFieldClass = DoubleFlatField
    CCDCorrectionClass = CCDFilter
    PaganinPhaseRetrievalClass = PaganinPhaseRetrieval
    UnsharpMaskClass = UnsharpMask
    ImageRotationClass = Rotation
    VerticalShiftClass = VerticalShift
    SinoBuilderClass = SinoBuilder
    SinoDeringerClass = MunchDeringer
    MLogClass = Log
    SinoNormalizationClass = SinoNormalization
    FBPClass = Backprojector
    HistogramClass = PartialHistogram

    def __init__(self, process_config, sub_region, logger=None, extra_options=None, phase_margin=None):
        """
        Initialize a "Chunked" pipeline.

        Parameters
        ----------
        processing_config: `ProcessConfig`
            Process configuration.
        sub_region: tuple
            Sub-region to process in the volume for this worker, in the format
            `(start_x, end_x, start_z, end_z)`.
        logger: `nabu.app.logger.Logger`, optional
            Logger class
        extra_options: dict, optional
            Advanced extra options.
        phase_margin: tuple, optional
            Margin to use when performing phase retrieval, in the form ((up, down), (left, right)).
            See also the documentation of PaganinPhaseRetrieval.
            If not provided, no margin is applied.


        Notes
        ------
        Using a `phase_margin` results in a lesser number of reconstructed slices.
        More specifically, if `phase_margin = (V, H)`, then there will be `delta_z - 2*V`
        reconstructed slices (if the sub-region is in the middle of the volume)
        or `delta_z - V` reconstructed slices (if the sub-region is on top or bottom
        of the volume).
        """
        self.logger = LoggerOrPrint(logger)
        self._set_params(process_config, sub_region, extra_options, phase_margin)
        self.set_subregion(sub_region)
        self._init_pipeline()


    def _set_params(self, process_config, sub_region, extra_options, phase_margin):
        self.process_config = process_config
        self.dataset_info = self.process_config.dataset_info
        self.dataset_infos = self.process_config.dataset_info # shorthand - deprecated
        self.processing_steps = self.process_config.processing_steps.copy()
        self.processing_options = self.process_config.processing_options
        self.sub_region = self._check_subregion(sub_region)
        self.delta_z = sub_region[-1] - sub_region[-2]
        self.chunk_size = self.delta_z
        self._set_phase_margin(phase_margin)
        self._set_extra_options(extra_options)
        self._callbacks = {}
        self._steps_name2component = {}
        self._steps_component2name = {}
        self._data_dump = {}
        self._resume_from_step = None


    @staticmethod
    def _check_subregion(sub_region):
        if len(sub_region) < 4:
            assert len(sub_region) == 2
            sub_region = (None, None) + sub_region
        if None in sub_region[-2:]:
            raise ValueError("Cannot set z_min or z_max to None")
        return sub_region


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {}
        advanced_options.update(extra_options)
        self.extra_options = advanced_options


    def _set_phase_margin(self, phase_margin):
        if phase_margin is None:
            phase_margin = ((0, 0), (0, 0))
        self._phase_margin_up = phase_margin[0][0]
        self._phase_margin_down = phase_margin[0][1]
        self._phase_margin_left = phase_margin[1][0]
        self._phase_margin_right = phase_margin[1][1]


    def set_subregion(self, sub_region):
        """
        Set a sub-region to process.

        Parameters
        ----------
        sub_region: tuple
            Sub-region to process in the volume, in the format
            `(start_x, end_x, start_z, end_z)` or `(start_z, end_z)`.
        """
        sub_region = self._check_subregion(sub_region)
        dz = sub_region[-1] - sub_region[-2]
        if dz != self.delta_z:
            raise ValueError(
                "Class was initialized for delta_z = %d but provided sub_region has delta_z = %d"
                % (self.delta_z, dz)
            )
        self.sub_region = sub_region
        self.z_min = sub_region[-2]
        self.z_max = sub_region[-1]


    def _compute_phase_kernel_margin(self):
        """
        Get the "margin" to pass to classes like PaganinPhaseRetrieval.
        In order to have a good accuracy for filter-based phase retrieval methods,
        we need to load extra data around the edges of each image. Otherwise,
        a default padding type is applied.
        """
        if not(self.use_radio_processing_margin):
            self._phase_margin = None
            return
        up_margin = self._phase_margin_up
        down_margin = self._phase_margin_down
        # Horizontal margin is not implemented
        left_margin, right_margin = (0, 0)
        self._phase_margin = ((up_margin, down_margin), (left_margin, right_margin))


    @property
    def use_radio_processing_margin(self):
        return ("phase" in self.processing_steps) or ("unsharp_mask" in self.processing_steps)


    def _get_phase_margin(self):
        if not(self.use_radio_processing_margin):
            return ((0, 0), (0, 0))
        return self._phase_margin


    def _get_cropped_radios(self):
        ((up_margin, down_margin), (left_margin, right_margin)) = self._phase_margin
        zslice = slice(up_margin or None, -down_margin or None)
        xslice = slice(left_margin or None, -right_margin or None)
        self._radios_cropped = self.radios[:, zslice, xslice]
        return self._radios_cropped


    @property
    def phase_margin(self):
        """
        Return the margin for phase retrieval in the form ((up, down), (left, right))
        """
        return self._get_phase_margin()


    @property
    def n_recs(self):
        """
        Return the final number of reconstructed slices.
        """
        n_recs = self.delta_z
        n_recs -= sum(self._get_phase_margin()[0])
        return n_recs


    def _get_process_name(self, kind="reconstruction"):
        # In the future, might be something like "reconstruction-<ID>"
        if kind == "reconstruction":
            return "reconstruction"
        elif kind == "histogram":
            return "histogram"
        return kind


    def _configure_dump(self, step_name):
        if step_name not in self.processing_steps:
            if step_name == "sinogram" and self.process_config._dump_sinogram:
                fname_full = self.process_config._dump_sinogram_file
            else:
                return
        else:
            if not self.processing_options[step_name].get("save", False):
                return
            fname_full = self.processing_options[step_name]["save_steps_file"]

        fname, ext = path.splitext(fname_full)
        dirname, file_prefix = path.split(fname)
        output_dir = path.join(dirname, file_prefix)
        file_prefix += str("_%04d" % self._get_image_start_index())

        self._data_dump[step_name] = WriterConfigurator(
            output_dir, file_prefix,
            file_format="hdf5",
            overwrite=True,
            logger=self.logger,
            nx_info = {
                "process_name": step_name,
                "processing_index": 0, # TODO
                "config": {
                    "processing_options": self.processing_options,
                    "nabu_config": self.process_config.nabu_config
                },
                "entry": getattr(self.dataset_info.dataset_scanner, "entry", None),
            }
        )


    def _configure_data_dumps(self):
        for step_name in self.processing_steps:
            self._configure_dump(step_name)
        # sinogram is a special keyword: not in processing_steps, but guaranteed to be before sinogram generation
        if self.process_config._dump_sinogram:
            self._configure_dump("sinogram")

    #
    # Callbacks
    #

    def register_callback(self, step_name, callback):
        """
        Register a callback for a pipeline processing step.

        Parameters
        ----------
        step_name: str
            processing step name
        callback: callable
            A function. It will be executed once the processing step `step_name`
            is finished. The function takes only one argument: the class instance.
        """
        if step_name not in self.processing_steps:
            raise ValueError(
                "'%s' is not in processing steps %s"
                % (step_name, self.processing_steps)
            )
        if step_name in self._callbacks:
            self._callbacks[step_name].append(callback)
        else:
            self._callbacks[step_name] = [callback]


    def _reshape_radios_after_phase(self):
        """
        Callback executed after phase retrieval, if margin != (0, 0).
        It modifies self.radios so that further processing will be done
        on the "inner part".
        """
        if sum(self._get_phase_margin()[0]) <= 0:
            return
        self._orig_radios = self.radios
        self.logger.debug(
            "Reshaping radios from %s to %s"
            % (str(self.radios.shape), str(self._radios_cropped.shape))
        )
        self.radios = self._radios_cropped

    #
    # Overwritten in inheriting classes
    #

    def _get_shape(self, step_name):
        """
        Get the shape to provide to the class corresponding to step_name.
        """
        if step_name == "flatfield":
            shape = self.radios.shape
        elif step_name == "double_flatfield":
            shape = self.radios.shape
        elif step_name == "rotate_projections":
            shape = self.radios.shape[1:]
        elif step_name == "phase":
            shape = self.radios.shape[1:]
        elif step_name == "ccd_correction":
            shape = self.radios.shape[1:]
        elif step_name == "unsharp_mask":
            shape = self.radios.shape[1:]
        elif step_name == "take_log":
            shape = self._radios_cropped_shape
        elif step_name == "radios_movements":
            shape = self._radios_cropped_shape
        elif step_name == "sino_normalization":
            shape = self._radios_cropped_shape
        elif step_name == "build_sino":
            shape = self._radios_cropped_shape
        elif step_name == "sino_rings_correction":
            shape = self.sino_builder.output_shape
        elif step_name == "reconstruction":
            shape = self.sino_builder.output_shape[1:]
        else:
            raise ValueError("Unknown processing step %s" % step_name)
        self.logger.debug("Data shape for %s is %s" % (step_name, str(shape)))
        return shape

    def _get_phase_output_shape(self):
        if not(self.use_radio_processing_margin):
            self._radios_cropped_shape = self.radios.shape
            return
        ((up_margin, down_margin), (left_margin, right_margin)) = self._phase_margin
        self._radios_cropped_shape = (
            self.radios.shape[0],
            self.radios.shape[1] - (up_margin + down_margin),
            self.radios.shape[2] - (left_margin + right_margin)
        )

    def _allocate_array(self, shape, dtype, name=None):
        return np.zeros(shape, dtype=dtype)

    def _allocate_sinobuilder_output(self):
        return self._allocate_array(self.sino_builder.output_shape, "f", name="sinos")

    def _allocate_recs(self, ny, nx):
        self.n_slices = self.radios.shape[1]  # TODO modify with vertical shifts
        if self.use_radio_processing_margin:
            self.n_slices -= sum(self.phase_margin[0])
        self.recs = self._allocate_array((self.n_slices, ny, nx), "f", name="recs")

    def _reset_memory(self):
        pass


    def _get_read_dump_subregion(self):
        read_opts = self.processing_options["read_chunk"]
        if read_opts.get("process_file", None) is None:
            return None
        dump_start_z, dump_end_z = read_opts["dump_start_z"], read_opts["dump_end_z"]
        relative_start_z = self.z_min - dump_start_z
        relative_end_z = relative_start_z + self.delta_z
        # (n_angles, n_z, n_x)
        subregion = (None, None, relative_start_z, relative_end_z, None, None)
        return subregion


    def _check_resume_from_step(self):
        if self._resume_from_step is None:
            return
        read_opts = self.processing_options["read_chunk"]
        expected_radios_shape = get_hdf5_dataset_shape(
            read_opts["process_file"],
            read_opts["process_h5_path"],
            sub_region=self._get_read_dump_subregion(),
        )
        # TODO check


    def _init_reader_finalize(self):
        """
        Method called after _init_reader
        """
        self._check_resume_from_step()
        self.radios = self.chunk_reader.data
        self._compute_phase_kernel_margin()
        self._get_phase_output_shape()


    def _process_finalize(self):
        """
        Method called once the pipeline has been executed
        """
        pass


    def _get_slice_start_index(self):
        return self.z_min + self._phase_margin_up

    _get_image_start_index = _get_slice_start_index

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
        self._init_radios_movements()
        self._init_mlog()
        self._init_sino_normalization()
        self._init_sino_builder()
        self._init_sino_rings_correction()
        self._prepare_reconstruction()
        self._init_reconstruction()
        self._init_histogram()
        self._init_writer()
        self._configure_data_dumps()

    @use_options("read_chunk", "chunk_reader")
    def _init_reader(self):
        if "read_chunk" not in self.processing_steps:
            raise ValueError("Cannot proceed without reading data")
        options = self.processing_options["read_chunk"]
        process_file = options.get("process_file", None)
        if process_file is None:
            # Standard case - start pipeline from raw data
            # ChunkReader always take a non-subsampled dictionary "files"
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
                process_file,
                options["process_h5_path"],
                sub_region=self._get_read_dump_subregion()
            )
            self._resume_from_step = options["step_name"]
            self.logger.debug(
                "Load subregion %s from file %s" % (str(self.chunk_reader.sub_region), self.chunk_reader.fname)
            )
        self._init_reader_finalize()

    @use_options("flatfield", "flatfield")
    def _init_flatfield(self, shape=None):
        if shape is None:
            shape = self._get_shape("flatfield")
        options = self.processing_options["flatfield"]

        distortion_correction = None
        if options["do_flat_distortion"]:
            self.logger.info("Flats distortion correction will be applied")
            estimation_kwargs = {}
            estimation_kwargs.update(options["flat_distortion_params"])
            estimation_kwargs["logger"] = self.logger
            distortion_correction = DistortionCorrection(
                estimation_method="fft-correlation",
                estimation_kwargs=estimation_kwargs,
                correction_method="interpn"
            )

        # FlatField parameter "radios_indices" must account for subsampling
        self.flatfield = self.FlatFieldClass(
            shape,
            flats=self.dataset_info.flats,
            darks=self.dataset_info.darks,
            radios_indices=options["projs_indices"],
            interpolation="linear",
            distortion_correction=distortion_correction,
            sub_region=self.sub_region,
            binning=options["binning"],
            convert_float=True
        )

    @use_options("double_flatfield", "double_flatfield")
    def _init_double_flatfield(self):
        options = self.processing_options["double_flatfield"]
        avg_is_on_log = (options["sigma"] is not None)
        result_url = None
        if options["processes_file"] not in (None, ""):
            result_url = DataUrl(
                file_path=options["processes_file"],
                data_path=(self.dataset_info.hdf5_entry or "entry") + "/double_flatfield/results/data",
            )
            self.logger.info("Loading double flatfield from %s" % result_url.file_path())
        self.double_flatfield = self.DoubleFlatFieldClass(
            self._get_shape("double_flatfield"),
            result_url=result_url,
            sub_region=self.sub_region,
            input_is_mlog=False,
            output_is_mlog=False,
            average_is_on_log=avg_is_on_log,
            sigma_filter=options["sigma"]
        )

    @use_options("ccd_correction", "ccd_correction")
    def _init_ccd_corrections(self):
        options = self.processing_options["ccd_correction"]
        self.ccd_correction = self.CCDCorrectionClass(
            self._get_shape("ccd_correction"),
            median_clip_thresh=options["median_clip_thresh"]
        )

    @use_options("phase", "phase_retrieval")
    def _init_phase(self):
        options = self.processing_options["phase"]
        # If unsharp mask follows phase retrieval, then it should be done
        # before cropping to the "inner part".
        # Otherwise, crop the data just after phase retrieval.
        if "unsharp_mask" in self.processing_steps:
            margin = None
        else:
            margin=self._phase_margin
        self.phase_retrieval = self.PaganinPhaseRetrievalClass(
            self._get_shape("phase"),
            distance=options["distance_m"],
            energy=options["energy_kev"],
            delta_beta=options["delta_beta"],
            pixel_size=options["pixel_size_m"],
            padding=options["padding_type"],
            margin=margin,
            fftw_num_threads=False, # TODO tune in advanced params of nabu config file
        )
        if self.phase_retrieval.use_fftw:
            self.logger.debug(
                "PaganinPhaseRetrieval using FFTW with %d threads"
                % self.phase_retrieval.fftw.num_threads
            )
        if "unsharp_mask" not in self.processing_steps:
            self.register_callback("phase", ChunkedPipeline._reshape_radios_after_phase)

    @use_options("unsharp_mask", "unsharp_mask")
    def _init_unsharp(self):
        options = self.processing_options["unsharp_mask"]
        self.unsharp_mask = self.UnsharpMaskClass(
            self._get_shape("unsharp_mask"),
            options["unsharp_sigma"], options["unsharp_coeff"],
            mode="reflect", method=options["unsharp_method"]
        )
        self.register_callback("unsharp_mask", ChunkedPipeline._reshape_radios_after_phase)

    @use_options("take_log", "mlog")
    def _init_mlog(self):
        options = self.processing_options["take_log"]
        self.mlog = self.MLogClass(
            self._get_shape("take_log"),
            clip_min=options["log_min_clip"],
            clip_max=options["log_max_clip"]
        )

    @use_options("rotate_projections", "projs_rot")
    def _init_radios_rotation(self):
        options = self.processing_options["rotate_projections"]
        center = options["center"]
        if center is None:
            nx, ny = self.dataset_info.radio_dims
            center = (nx/2 - 0.5, ny/2 - 0.5)
        center = (center[0], center[1] - self.z_min)
        self.projs_rot = self.ImageRotationClass(
            self._get_shape("rotate_projections"),
            options["angle"],
            center=center,
            mode="edge",
            reshape=False
        )
        self._tmp_rotated_radio = self._allocate_array(
            self._get_shape("rotate_projections"), "f", name="tmp_rotated_radio"
        )

    @use_options("radios_movements", "radios_movements")
    def _init_radios_movements(self):
        options = self.processing_options["radios_movements"]
        self._vertical_shifts = options["translation_movements"][:, 1]
        self.radios_movements = self.VerticalShiftClass(
            self._get_shape("radios_movements"),
            self._vertical_shifts
        )

    @use_options("sino_normalization", "sino_normalization")
    def _init_sino_normalization(self):
        options = self.processing_options["sino_normalization"]
        self.sino_normalization = self.SinoNormalizationClass(
            kind=options["method"],
            radios_shape=self._get_shape("sino_normalization"),
        )

    @use_options("build_sino", "sino_builder")
    def _init_sino_builder(self):
        options = self.processing_options["build_sino"]
        self.sino_builder = self.SinoBuilderClass(
            radios_shape=self._get_shape("build_sino"),
            rot_center=options["rotation_axis_position"],
            halftomo=options["enable_halftomo"],
        )
        if not(options["enable_halftomo"]):
            self._sinobuilder_copy = False
            self._sinobuilder_output = None
            self.sinos = None
        else:
            self._sinobuilder_copy = True
            self.sinos = self._allocate_sinobuilder_output()
            self._sinobuilder_output = self.sinos

    @use_options("sino_rings_correction", "sino_deringer")
    def _init_sino_rings_correction(self):
        options = self.processing_options["sino_rings_correction"]
        fw_params = extract_parameters(options["user_options"])
        fw_sigma = fw_params.pop("sigma", 1.)
        self.sino_deringer = self.SinoDeringerClass(
            fw_sigma,
            sinos_shape=self._get_shape("sino_rings_correction"),
            **fw_params
        )

    # this should be renamed, as it could be confused with _init_reconstruction. What about _get_reconstruction_array ?
    @use_options("reconstruction", "reconstruction")
    def _prepare_reconstruction(self):
        options = self.processing_options["reconstruction"]
        x_s, x_e = options["start_x"], options["end_x"]
        y_s, y_e = options["start_y"], options["end_y"]
        self._rec_roi = (x_s, x_e + 1, y_s, y_e + 1)
        self._allocate_recs(y_e - y_s + 1, x_e - x_s + 1)


    @use_options("reconstruction", "reconstruction")
    def _init_reconstruction(self):
        options = self.processing_options["reconstruction"]
        if self.sino_builder is None:
            raise ValueError("Reconstruction cannot be done without build_sino")
        if self.FBPClass is None:
            raise ValueError("No usable FBP module was found")

        if options["enable_halftomo"]:
            rot_center = options["rotation_axis_position_halftomo"]
        else:
            rot_center = options["rotation_axis_position"]
        if self.sino_builder._halftomo_flip:
            rot_center = self.sino_builder.rot_center

        self.reconstruction = self.FBPClass(
            self._get_shape("reconstruction"),
            angles=options["angles"],
            rot_center=rot_center,
            filter_name=options["fbp_filter_type"],
            slice_roi=self._rec_roi,
            padding_mode=options["padding_type"],
            extra_options={
                "scale_factor": 1./options["pixel_size_cm"],
                "axis_correction": options["axis_correction"],
                "centered_axis": options["centered_axis"],
                "clip_outer_circle": options["clip_outer_circle"],
            }
        )
        if options["fbp_filter_type"] is None:
            self.reconstruction.fbp = self.reconstruction.backproj

    @use_options("histogram", "histogram")
    def _init_histogram(self):
        options = self.processing_options["histogram"]
        self.histogram = self.HistogramClass(
            method="fixed_bins_number", num_bins=options["histogram_bins"]
        )

    @use_options("save", "writer")
    def _init_writer(self):
        options = self.processing_options["save"]
        file_prefix = options["file_prefix"]
        output_dir = path.join(
            options["location"],
            file_prefix
        )
        nx_info = None
        self._hdf5_output = is_hdf5_extension(options["file_format"], errors=False)
        if self._hdf5_output:
            fname_start_index = None
            file_prefix += str("_%04d" % self._get_slice_start_index())
            entry = getattr(self.dataset_info.dataset_scanner, "entry", None)
            nx_info = {
                "process_name": self._get_process_name(),
                "processing_index": 0,
                "config": {
                    # "processing_options": self.processing_options, # Takes too much time to write, not useful for partial files
                    "nabu_config": self.process_config.nabu_config,
                },
                "entry": entry,
            }
            self._histogram_processing_index = nx_info["processing_index"] + 1
        else:
            fname_start_index = self._get_slice_start_index()
            self._histogram_processing_index = 1
        writer_options = {}
        if options["tiff_single_file"]:
            writer_options = {
                "tiff_single_file": options["tiff_single_file"],
                "single_tiff_initialized": getattr(self.process_config, "single_tiff_initialized", False),
            }
            self.process_config.single_tiff_initialized = True
        self._writer_configurator = WriterConfigurator(
            output_dir, file_prefix,
            file_format=options["file_format"],
            overwrite=options["overwrite"],
            start_index=fname_start_index,
            logger=self.logger,
            nx_info=nx_info,
            write_histogram=("histogram" in self.processing_steps),
            histogram_entry=getattr(self.dataset_info.dataset_scanner, "entry", "entry"),
            writer_options=writer_options,
            extra_options={
                "jpeg2000_compression_ratio": options["jpeg2000_compression_ratio"],
                "float_clip_values": options["float_clip_values"],
            }
        )
        self.writer = self._writer_configurator.writer
        self._writer_exec_args = self._writer_configurator._writer_exec_args
        self._writer_exec_kwargs = self._writer_configurator._writer_exec_kwargs
        self.histogram_writer = self._writer_configurator.get_histogram_writer()


    #
    # Pipeline re-initialization
    #

    def _reset_sub_region(self, sub_region):
        self.set_subregion(sub_region)
        self._reset_reader_subregion()
        self._reset_flatfield()

    def _reset_flatfield(self):
        self._init_flatfield()

    #
    # Pipeline execution
    #

    @pipeline_step("chunk_reader", "Reading data")
    def _read_data(self):
        self.logger.debug("Region = %s" % str(self.sub_region))
        t0 = time()
        self.chunk_reader.load_data()
        el = time() - t0

        shp = self.chunk_reader.data.shape
        itemsize = self.chunk_reader.dtype.itemsize if hasattr(self.chunk_reader, "dtype") else 4
        GB = np.prod(shp) * itemsize / 1e9
        self.logger.info(
            "Read subvolume %s (%.2f GB) in %.2f s: %.3f GB/s"
            % (str(shp), GB, el, GB/el)
        )

    def _reset_reader_subregion(self):
        if self._resume_from_step is None:
            self.chunk_reader._set_subregion(self.sub_region)
            self.chunk_reader._init_reader()
            self.chunk_reader._loaded = False
        else:
            self.chunk_reader._set_subregion(self._get_read_dump_subregion())
            self.chunk_reader._loaded = False


    @pipeline_step("flatfield", "Applying flat-field")
    def _flatfield(self):
        self.flatfield.normalize_radios(self.radios)

    @pipeline_step("double_flatfield", "Applying double flat-field")
    def _double_flatfield(self, radios=None):
        if radios is None:
            radios = self.radios
        self.double_flatfield.apply_double_flatfield(radios)

    @pipeline_step("ccd_correction", "Applying CCD corrections")
    def _ccd_corrections(self, radios=None):
        if radios is None:
            radios = self.radios
        _tmp_radio = self._allocate_array(radios.shape[1:], "f", name="tmp_ccdcorr_radio")
        for i in range(radios.shape[0]):
            self.ccd_correction.median_clip_correction(
                radios[i], output=_tmp_radio
            )
            radios[i][:] = _tmp_radio[:]

    @pipeline_step("projs_rot", "Rotating projections")
    def _rotate_projections(self, radios=None):
        if radios is None:
            radios = self.radios
        tmp_radio = self._tmp_rotated_radio
        for i in range(radios.shape[0]):
            self.projs_rot.rotate(radios[i], output=tmp_radio)
            radios[i][:] = tmp_radio[:]

    @pipeline_step("phase_retrieval", "Performing phase retrieval")
    def _retrieve_phase(self):
        if "unsharp_mask" in self.processing_steps:
            output = self.radios
        else:
            self._get_cropped_radios()
            output = self._radios_cropped
        for i in range(self.radios.shape[0]):
            self.phase_retrieval.apply_filter(
                self.radios[i], output=output[i]
            )

        # TEST
        # def retrieve_phase_func(radio_and_output):
        #     radio, output = radio_and_output
        #     self.phase_retrieval.apply_filter(
        #         radio, output=output
        #     )
        # from multiprocessing.pool import ThreadPool
        # with ThreadPool(10) as T:
        #     T.map(retrieve_phase_func, zip(self.radios, output))


    @pipeline_step("unsharp_mask", "Performing unsharp mask")
    def _apply_unsharp(self):
        for i in range(self.radios.shape[0]):
            self.radios[i] = self.unsharp_mask.unsharp(self.radios[i])
        self._get_cropped_radios()

    @pipeline_step("mlog", "Taking logarithm")
    def _take_log(self):
        self.mlog.take_logarithm(self.radios)

    @pipeline_step("radios_movements", "Applying radios movements")
    def _radios_movements(self, radios=None):
        if radios is None:
            radios = self.radios
        self.radios_movements.apply_vertical_shifts(
            radios, list(range(radios.shape[0]))
        )

    @pipeline_step("sino_normalization", "Normalizing sinograms")
    def _normalize_sinos(self, radios=None):
        if radios is None:
            radios = self.radios
        sinos = radios.transpose((1, 0, 2))
        self.sino_normalization.normalize(sinos)

    def _dump_sinogram(self, radios=None):
        if radios is None:
            radios = self.radios
        self._dump_data_to_file("sinogram", data=radios)

    @pipeline_step("sino_builder", "Building sinograms")
    def _build_sino(self, radios=None):
        if radios is None:
            radios = self.radios
        # Either a new array (previously allocated in "_sinobuilder_output"),
        # or a view of "radios"
        self.sinos = self.sino_builder.radios_to_sinos(
            radios,
            output=self._sinobuilder_output,
            copy=self._sinobuilder_copy
        )

    @pipeline_step("sino_deringer", "Removing rings on sinograms")
    def _destripe_sinos(self, sinos=None):
        if sinos is None:
            sinos = self.sinos
        self.sino_deringer.remove_rings(sinos)

    @pipeline_step("reconstruction", "Reconstruction")
    def _reconstruct(self, sinos=None):
        if sinos is None:
            sinos = self.sinos
        for i in range(sinos.shape[0]):
            self.reconstruction.fbp(
                sinos[i], output=self.recs[i]
            )

    @pipeline_step("histogram", "Computing histogram")
    def _compute_histogram(self, data=None):
        if data is None:
            data = self.recs
        self.recs_histogram = self.histogram.compute_histogram(data)

    @pipeline_step("writer", "Saving data")
    def _write_data(self, data=None):
        if data is None:
            data = self.recs
        self.writer.write(data, *self._writer_exec_args, **self._writer_exec_kwargs)
        self.logger.info("Wrote %s" % self.writer.get_filename())
        self._write_histogram()

    def _write_histogram(self):
        if "histogram" not in self.processing_steps:
            return
        self.logger.info("Saving histogram")
        self.histogram_writer.write(
            hist_as_2Darray(self.recs_histogram),
            self._get_process_name(kind="histogram"),
            processing_index=self._histogram_processing_index,
            config={
                "file": path.basename(self.writer.get_filename()),
                "bins": self.processing_options["histogram"]["histogram_bins"],
            }
        )

    def _dump_data_to_file(self, step_name, data=None):
        if step_name not in self._data_dump:
            return
        if data is None:
            data = self.radios
        writer = self._data_dump[step_name]
        self.logger.info("Dumping data to %s" % writer.fname)
        writer.write_data(data)


    def _process_chunk(self):
        self._flatfield()
        self._double_flatfield()
        self._ccd_corrections()
        self._rotate_projections()
        self._retrieve_phase()
        self._apply_unsharp()
        self._take_log()
        self._radios_movements()
        self._normalize_sinos()
        self._dump_sinogram()
        self._build_sino()
        self._destripe_sinos()
        self._reconstruct()
        self._compute_histogram()
        self._write_data()
        self._process_finalize()


    def process_chunk(self, sub_region=None):
        if sub_region is not None:
            self._reset_sub_region(sub_region)
            self._reset_memory()
            self._init_writer()
            self._init_double_flatfield()
            self._configure_data_dumps()
        self._read_data()
        self._process_chunk()
