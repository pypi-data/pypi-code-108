from math import ceil
import numpy as np
from ...utils import deprecated
from ...preproc.ccd_cuda import CudaLog, CudaCCDFilter
from ...preproc.flatfield_cuda import CudaFlatFieldDataUrls
from ...preproc.shift import VerticalShift
from ...preproc.shift_cuda import CudaVerticalShift
from ...preproc.double_flatfield import DoubleFlatField
from ...preproc.double_flatfield_cuda import CudaDoubleFlatField
from ...preproc.phase_cuda import CudaPaganinPhaseRetrieval
from ...reconstruction.sinogram_cuda import CudaSinoBuilder, CudaSinoNormalization
from ...reconstruction.sinogram import SinoBuilder, SinoNormalization
from ...reconstruction.rings_cuda import CudaMunchDeringer
from ...misc.unsharp_cuda import CudaUnsharpMask
from ...misc.rotation_cuda import CudaRotation
from ...misc.histogram_cuda import CudaPartialHistogram
from ...reconstruction.fbp import Backprojector
from ...cuda.utils import get_cuda_context, __has_pycuda__, __pycuda_error_msg__, replace_array_memory
from ..utils import pipeline_step
from .chunked import ChunkedPipeline

if __has_pycuda__:
    import pycuda.gpuarray as garray


class CudaChunkedPipeline(ChunkedPipeline):
    """
    Cuda backend of ChunkedPipeline
    """

    backend = "cuda"
    FlatFieldClass = CudaFlatFieldDataUrls
    DoubleFlatFieldClass = CudaDoubleFlatField
    CCDCorrectionClass = CudaCCDFilter
    PaganinPhaseRetrievalClass = CudaPaganinPhaseRetrieval
    UnsharpMaskClass = CudaUnsharpMask
    ImageRotationClass = CudaRotation
    VerticalShiftClass = CudaVerticalShift
    SinoBuilderClass = CudaSinoBuilder
    SinoDeringerClass = CudaMunchDeringer
    MLogClass = CudaLog
    FBPClass = Backprojector
    HistogramClass = CudaPartialHistogram
    SinoNormalizationClass = CudaSinoNormalization

    def __init__(self, process_config, sub_region, logger=None, extra_options=None, phase_margin=None, cuda_options=None):
        self._init_cuda(cuda_options)
        super().__init__(
             process_config, sub_region,
             logger=logger, extra_options=extra_options, phase_margin=phase_margin
        )
        self._register_callbacks()


    def _init_cuda(self, cuda_options):
        if not(__has_pycuda__):
            raise ImportError(__pycuda_error_msg__)
        cuda_options = cuda_options or {}
        self.ctx = get_cuda_context(**cuda_options)
        self._d_radios = None
        self._d_sinos = None
        self._d_recs = None


    def _allocate_array(self, shape, dtype, name=None):
        name = name or "tmp" # should be mandatory
        d_name = "_d_" + name
        d_arr = getattr(self, d_name, None)
        if d_arr is None:
            self.logger.debug("Allocating %s: %s" % (name, str(shape)))
            d_arr = garray.zeros(shape, dtype)
            setattr(self, d_name, d_arr)
        return d_arr


    def _transfer_radios_to_gpu(self):
        self._allocate_array(self.radios.shape, "f", name="radios")
        self._d_radios.set(self.radios)
        self._h_radios = self.radios
        self.radios = self._d_radios

    def _process_finalize(self):
        self.radios = self._h_radios

    #
    # Callbacks
    #

    def _read_data_callback(self):
        self.logger.debug("Transfering radios to GPU")
        self._transfer_radios_to_gpu()

    def _rec_callback(self):
        self.logger.debug("Getting reconstructions from GPU")
        self.recs = self.recs.get()

    def _saving_callback(self):
        self.recs = self._d_recs
        self.radios = self._h_radios


    def _register_callbacks(self):
        self.register_callback("read_chunk", CudaChunkedPipeline._read_data_callback)
        if self.reconstruction is not None:
            self.register_callback("reconstruction", CudaChunkedPipeline._rec_callback)
        if self.writer is not None:
            self.register_callback("save", CudaChunkedPipeline._saving_callback)


    #
    # Pipeline execution (class specialization)
    #

    @pipeline_step("histogram", "Computing histogram")
    def _compute_histogram(self, data=None):
        if data is None:
            data = self._d_recs
        self.recs_histogram = self.histogram.compute_histogram(data)


    def _dump_data_to_file(self, step_name, data=None):
        if data is None:
            data = self.radios
        if step_name not in self._data_dump:
            return
        if isinstance(data, garray.GPUArray):
            data = data.get()
        super()._dump_data_to_file(step_name, data=data)


class CudaChunkedPipelineLimitedMemory(CudaChunkedPipeline):
    """
    Cuda backend of ChunkedPipeline, adapted to the case where not all the
    images fit in device memory.

    The classes acting on radios are not instantiated with the same shape as
    the classes acting on sinograms.
    """

    # In this case, the "build sinogram" step is best done on host to avoid
    # extraneous CPU<->GPU copies, and save some GPU memory.
    SinoBuilderClass = SinoBuilder
    # Same for DoubleFlatField
    DoubleFlatFieldClass = DoubleFlatField
    # VerticalShifts is simpler on host. It should be done on GPU if it slows down the process too much
    VerticalShiftClass = VerticalShift
    # SinoNormalization is done on host (in-place)
    SinoNormalizationClass = SinoNormalization

    def __init__(self, process_config, sub_region, chunk_size, logger=None, extra_options=None, phase_margin=None, cuda_options=None):
        """
        Initialize a Chunked pipeline with cuda backend, with limited memory
        setting.

        Important
        ----------
        The parameter `chunk_size` must be such that `chunk_size * Nx * Na` voxel
        can fit in device memory, especially when using Cuda/OpenCL.
        If not provided, `chunk_size` is equal to `delta_z = sub_region[-1] - sub_region[-2]`.
        So for wide detectors with a big number of radios, this is likely to fail.
        Providing a `chunk_size` accordingly enables to process the images by groups
        (see Notes below).
        This class always assumes that `delta_z * Nx * Na* fits in RAM (but not
        necessarily in GPU memory).


        Notes
        ------
        Let `Dz` be the subvolume height (i.e `sub_region[-1] - sub_region[-2]`),
        `Nx` the number of pixels horizontally, and `Na` the number of angles (radios),
        as illustrated below::


                     _________________
                    /                /|
                   /                / |
                  /________________/  |
                 |                 |  /
              Dz |                 | / Na
                 |_________________|/
                       Nx


        If the subvolume to process (`Dz * Nx * Na` voxels) is too big to fit in device memory,
        then images are processed by "groups" instead of processing the whole
        subvolume in one memory chunk.
        More precisely:
           - Radios are are processed by groups of `G` "vertical images"
             where `G` is such that `G * Dz * Nx` fits in memory
             (i.e `G * Dz * Nx = chunk_size * Nx * Na`)
           - Sinograms are processed by group of `chunk_size` "horizontal images"
             since by hypothesis `chunk_size * Nx * Na` fits in memory.
        """
        self._chunk_size = chunk_size
        super().__init__(
             process_config, sub_region,
             logger=logger, extra_options=extra_options, phase_margin=phase_margin,
             cuda_options=cuda_options
        )
        self._allocate_radios()
        self._h_recs = None
        self._h_sinos = None
        self._old_flatfield = None
        # This is a current limitation.
        # Things are a bit tricky as chunk_size and delta_z would have to be
        # divided by binning_z, but then the group size has to be re-calculated.
        # On the other hand, it makes little sense to use this class
        # for other use cases than full-resolution reconstruction...
        if self.processing_options["read_chunk"].get("binning", (1, 1))[-1] > 1:
            raise ValueError("Binning in z is not supported with this class")
        #

    def _get_shape(self, step_name):
        """
        Get the shape to provide to the class corresponding to step_name.
        """
        n_a = self.dataset_info.n_angles
        margin_v = sum(self._get_phase_margin()[0])
        if step_name == "flatfield":
            # Flat-field is done on device. Shape: (group_size, delta_z, width)
            shape = self.radios_group_shape
        elif step_name == "double_flatfield":
            # Double Flat-field is done on host. Shape:  (n_angles, delta_z, width)
            shape = (n_a, ) + self.radios.shape[1:]
        elif step_name == "ccd_correction":
            shape = self.radios.shape[1:]
        elif step_name == "rotate_projections":
            shape = self.radios.shape[1:]
        elif step_name == "phase":
            # Phase retrieval is done on device. Shape: (group_size, delta_z, width)
            shape = self.radios.shape[1:]
        elif step_name == "unsharp_mask":
            shape = self.radios.shape[1:]
        elif step_name == "take_log":
            # Done on device
            shape = self._radios_cropped_shape
        elif step_name == "radios_movements":
            shape = self._radios_cropped_shape
        elif step_name == "sino_normalization":
            shape = self._radios_cropped_shape
        elif step_name == "build_sino":
            shape = (n_a, self.n_recs, self.radios_shape[-1])
        elif step_name == "sino_rings_correction":
            shape = self.sino_builder.output_shape[1:]
        elif step_name == "reconstruction":
            shape = self.sino_builder.output_shape[1:]
        else:
            raise ValueError("Unknown processing step %s" % step_name)
        self.logger.debug("Data shape for %s is %s" % (step_name, str(shape)))
        return shape

    def _get_phase_output_shape(self):
        if not(self.use_radio_processing_margin):
            self._radios_cropped_shape = self.radios_group_shape
            return
        ((up_margin, down_margin), (left_margin, right_margin)) = self._phase_margin
        self._radios_cropped_shape = (
            self.radios_group_shape[0],
            self.radios_group_shape[1] - (up_margin + down_margin),
            self.radios_group_shape[2] - (left_margin + right_margin)
        )

    def _init_reader_finalize(self):
        """
        Method called after _init_reader.
        In this case:
           - Reader gets all the data in memory (n_angles, delta_z, n_x)
           - CCD processing classes handle groups of images: (group_size, delta_z, n_x)
           - Sino processing classes handle stack of sinos (chunk_size, n_angles, n_x)
        """
        self.chunk_size = self._chunk_size
        n_a = self.dataset_info.n_angles
        self.radios_group_size = min(
            (n_a * self.chunk_size) // self.delta_z,
            n_a
        )
        self._n_radios_groups = ceil(n_a / self.radios_group_size)

        self._check_resume_from_step()
        self.radios = self.chunk_reader.data

        # self.radios: (n_angles, delta_z, n_x) - fits in RAM but not in GPU memory
        # self._configure_resume_from_step()
        # (group_size, delta_z, n_x) - fits in GPU mem
        self.radios_group_shape = (self.radios_group_size, ) + self.radios.shape[1:]
        # passed to CCD processing classes
        self.radios_shape = self.radios_group_shape
        self._flatfield_is_done = False
        if "flatfield" in self.processing_steps:
            # We need to update the projections indices passed to FlatField
            # for each group of radios
            ff_opts = self.processing_options["flatfield"]
            self._ff_proj_indices = ff_opts["projs_indices"]
            self._old_ff_proj_indices = self._ff_proj_indices.copy()
            ff_opts["projs_indices"] = ff_opts["projs_indices"][:self.radios_group_size]
        self._compute_phase_kernel_margin()
        self._get_phase_output_shape()
        # Processing acting on sinograms will be done later
        self._processing_steps = self.processing_steps.copy()
        for step in ["build_sino", "sino_rings_correction", "reconstruction", "save"]:
            if step in self.processing_steps:
                self.processing_steps.remove(step)
        self._partial_histograms = []

    def _allocate_radios(self):
        self._allocate_array(self.radios_group_shape, "f", name="radios")
        self._h_radios = self.radios # (n_angles, delta_z, width) (does not fit in GPU mem)
        self.radios = self._d_radios # (radios_group_size, delta_z, width) (fits in GPU mem)

    def _allocate_sinobuilder_output(self):
        # Allocate device sinograms
        self._allocate_array(
            (self.chunk_size, ) + self.sino_builder.output_shape[1:], "f", name="sinos"
        )
        if self._h_sinos is None:
            self._h_sinos = np.zeros(self.sino_builder.output_shape, "f")
        self._sinobuilder_output = self._h_sinos
        return self._h_sinos

    def _allocate_recs(self, ny, nx):
        self.recs = self._allocate_array((self.chunk_size, ny, nx), "f", name="recs")

    def _register_callbacks(self):
        # No callbacks are registered for this subclass
        pass
        # self.register_callback("read_chunk", CudaChunkedPipelineLimitedMemory._read_data_callback)

    def _configure_data_dumps(self):
        do_data_dump = False
        for step_name in self.processing_steps:
            if self.processing_options[step_name].get("save", False):
                do_data_dump = True
                break
        if not do_data_dump and not self.process_config._dump_sinogram:
            return
        self.logger.warning(
            "With the mode '%s', saving intermediate steps can only be used to save final pre-processed radios"
            % self.__class__.__name__
        )
        self._configure_dump("sinogram")


    def _process_finalize(self):
        # release cuda memory
        if self._d_sinos is not None:
            replace_array_memory(self._d_sinos, (1,))
            self._d_sinos = None
        if self._d_recs is not None:
            replace_array_memory(self._d_recs, (1,))
            self._d_recs = None
        # re-allocate _d_radios for processing a new chunk
        self.radios = self._h_radios
        self._allocate_radios()
        self.flatfield = self._old_flatfield
        self._flatfield_is_done = False
        if "flatfield" in self._processing_steps:
            self.processing_options["flatfield"]["projs_indices"] = self._old_ff_proj_indices

    def _reset_flatfield(self):
        # Done by _reinit_flatfield at each new radios group
        pass

    def _reinit_flatfield(self, start_idx, end_idx, transfer_size):
        if "flatfield" in self.processing_steps:
            # We need to update the projections indices passed to FlatField
            # for each group of radios
            ff_opts = self.processing_options["flatfield"]
            ff_opts["projs_indices"] = self._ff_proj_indices[start_idx:end_idx]
            self._init_flatfield(shape=(transfer_size, ) + self.radios_shape[1:])

    def _flatfield_radios_group(self, start_idx, end_idx, transfer_size):
        self._reinit_flatfield(start_idx, end_idx, transfer_size)
        self._flatfield()

    def _apply_flatfield_and_dff(self, n_groups, group_size, n_images):
        """
        If double flat-field is activated, apply flat-field + double flat-field.
        Otherwise, do nothing and leave the flat-field for later "group processing"
        """
        if "double_flatfield" not in self.processing_steps:
            return
        for i in range(n_groups):
            self.logger.info("processing group %d/%d" % (i+1, n_groups))
            start_idx = i * group_size
            end_idx = min((i + 1) * group_size, n_images)
            transfer_size = end_idx - start_idx
            # Copy H2D
            self._d_radios[:transfer_size, :, :] = self._h_radios[start_idx:end_idx, :, :]
            # Process a group of radios (radios_group_size, delta_z, width)
            self._old_radios = self.radios
            self.radios = self.radios[:transfer_size]
            self._flatfield_radios_group(start_idx, end_idx, transfer_size)
            self.radios = self._old_radios
            # Copy D2H
            self._d_radios[:transfer_size, :, :].get(ary=self._h_radios[start_idx:end_idx])
        # Here flat-field has been applied on all radios (n_angles, delta_z, n_x).
        # Now apply double FF on host.
        self._double_flatfield(radios=self._h_radios)
        self._flatfield_is_done = True

    def _compute_histogram_partial(self, data=None):
        if data is None:
            data = self._d_recs
        if self.histogram is not None:
            self._compute_histogram(data=data)
            self._partial_histograms.append(self.recs_histogram)

    def _merge_partial_histograms(self):
        if self.histogram is None:
            return
        self.recs_histogram = self.histogram.merge_histograms(self._partial_histograms)

    def _process_chunk_ccd(self):
        """
        Perform the processing in the "CCD space" (on radios)
        """
        n_groups = self._n_radios_groups
        group_size = self.radios_group_size
        n_images = self._h_radios.shape[0]

        self._apply_flatfield_and_dff(n_groups, group_size, n_images)

        for i in range(n_groups):
            self.logger.info("processing group %d/%d" % (i+1, n_groups))
            start_idx = i * group_size
            end_idx = min((i + 1) * group_size, n_images)
            transfer_size = end_idx - start_idx
            # Copy H2D
            self._d_radios[:transfer_size, :, :] = self._h_radios[start_idx:end_idx, :, :]
            # Process a group of radios (radios_group_size, delta_z, width)
            self._old_radios = self.radios
            self.radios = self.radios[:transfer_size]
            if not(self._flatfield_is_done):
                self._flatfield_radios_group(start_idx, end_idx, transfer_size)
            self._ccd_corrections()
            self._rotate_projections()
            self._retrieve_phase()
            self._apply_unsharp()
            self._take_log()
            self.radios = self._old_radios
            # Copy D2H
            self._d_radios[:transfer_size, :, :].get(ary=self._h_radios[start_idx:end_idx])
        self._radios_movements(radios=self._h_radios)
        self.logger.debug("End of processing steps on radios")
        if self.process_config._dump_sinogram:
            ((up_margin, down_margin), (left_margin, right_margin)) = self._get_phase_margin()
            down_margin = -down_margin or None
            right_margin = -right_margin or None
            self._dump_sinogram(
                radios=self._h_radios[:, up_margin:down_margin, left_margin:right_margin]
            )

        # Restore original processing steps
        self.processing_steps = self._processing_steps
        # Initialize sino builder
        if "build_sino" in self.processing_steps:
            self._init_sino_builder()
            # release cuda memory of _d_radios
            # We could use the same array as gpudata=self._d_radios.gpudata
            # to create self._d_sinos, but it does not behave well when
            # delta_z is not a multiple of chunk_size.
            replace_array_memory(self._d_radios, (1,))
            self._d_radios = None
            self._d_sinos = garray.zeros(
                (self.chunk_size, ) + self.sino_builder.output_shape[1:],
                "f"
            )

    def _process_chunk_sinos(self):
        """
        Perform the processing in the "sinograms space"
        """
        # TODO support write earlier than reconstruction
        if "reconstruction" not in self.processing_steps:
            return
        self.logger.debug("Initializing processing on sinos")
        self._init_sino_rings_correction()
        self._prepare_reconstruction()
        self._init_reconstruction()
        self._init_writer()

        # Crop radios to inner "phase margin", if needed
        ((up_margin, down_margin), (left_margin, right_margin)) = self._get_phase_margin()
        self._orig_h_radios = self._h_radios
        down_margin = -down_margin or None
        right_margin = -right_margin or None
        self._h_radios = self._h_radios[:, up_margin:down_margin, left_margin:right_margin]
        #

        if self._h_recs is None:
            self._h_recs = np.zeros((self.n_recs, ) + self.recs.shape[1:], "f")

        # Normalize sinos on host
        self._normalize_sinos(radios=self._h_radios)

        # Build sinograms on host.
        # Doing it here rather than in the following loop is simpler but uses more memory.
        # In the loop, "self.sino_builder" has to be re-initialized
        # because the shape might change at the last chunk.
        self._build_sino(radios=self._h_radios)

        n_groups = ceil(self.n_recs / self.chunk_size)
        group_size = self.chunk_size
        for i in range(n_groups):
            self.logger.info("processing stack %d/%d" % (i+1, n_groups))
            start_idx = i * group_size
            end_idx = min((i + 1) * group_size, self.n_recs)
            transfer_size = end_idx - start_idx
            # Copy H2D
            # pycuda does not support copy where "order" is not the same
            # (self.sinos might be a view on self.radios)
            sinos = self.sinos[start_idx:end_idx] # self.sinos is a numpy array
            if not(self._sinobuilder_copy) and not(self.sinos.flags["C_CONTIGUOUS"]):
                sinos = np.ascontiguousarray(sinos)
            #
            self._d_sinos[:transfer_size, :, :] = sinos[:, :, :]
            # Process stack of sinograms (chunk_size, n_angles, width)
            self._destripe_sinos(sinos=self._d_sinos)
            self._reconstruct(sinos=self._d_sinos)
            self._compute_histogram_partial(data=self._d_recs[:transfer_size])
            # Copy D2H
            self._d_recs[:transfer_size].get(ary=self._h_recs[start_idx:end_idx])
        self.logger.debug("End of processing steps on sinos")
        self._h_radios = self._orig_h_radios
        self._merge_partial_histograms()
        # Write
        self._write_data(data=self._h_recs)

    def _process_chunk(self):
        self._process_chunk_ccd()
        self._process_chunk_sinos()
        self._process_finalize()
