import numpy as np
from ...cuda.utils import __has_pycuda__, __pycuda_error_msg__, get_cuda_context
from ...preproc.ccd_cuda import CudaLog, CudaCCDFilter
from ...preproc.flatfield_cuda import CudaFlatFieldDataUrls
from ...preproc.shift_cuda import CudaVerticalShift
from ...preproc.ctf_cuda import CudaCTFPhaseRetrieval
from ...preproc.ctf import GeoPars
from ...preproc.double_flatfield_cuda import CudaDoubleFlatField
from ...preproc.phase_cuda import CudaPaganinPhaseRetrieval
from ...reconstruction.sinogram import SinoBuilder
from ...reconstruction.sinogram_cuda import CudaSinoBuilder, CudaSinoNormalization
from ...reconstruction.rings_cuda import CudaMunchDeringer
from ...misc.unsharp_cuda import CudaUnsharpMask
from ...misc.rotation_cuda import CudaRotation
from ...misc.histogram_cuda import CudaPartialHistogram
from ...reconstruction.fbp import Backprojector
from .grouped import GroupedPipeline, SinoStackPipeline
from .chunked_cuda import CudaChunkedPipeline
from ..utils import pipeline_step

class CudaGroupedPipeline(GroupedPipeline):
    """
    Cuda backend of GroupedPipeline
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

    def __init__(self, process_config, images_group, sub_region=None, logger=None, extra_options=None, cuda_options=None):
        self._init_cuda(cuda_options)
        super().__init__(
             process_config, images_group,
             sub_region=sub_region, logger=logger, extra_options=extra_options
        )

    # TODO base class ?
    def _init_cuda(self, cuda_options):
        if not(__has_pycuda__):
            raise ImportError(__pycuda_error_msg__)
        cuda_options = cuda_options or {}
        self.ctx = get_cuda_context(**cuda_options)
        # self._d_radios = None

    _allocate_array = CudaChunkedPipeline._allocate_array # TODO base class ?


    def _init_pipeline(self):
        super()._init_pipeline()
        self._allocate_array(self.radios.shape, "f", name="radios")


    # overwrite
    def _init_ctf_phase(self):
        options = self.processing_options["phase"]
        geo_pars_params = options["ctf_geo_pars"].copy()
        geo_pars_params["logger"] = self.logger
        geo_pars = GeoPars(**geo_pars_params)
        self.phase_retrieval = CudaCTFPhaseRetrieval(
            self.radios.shape[1:],
            geo_pars,
            options["delta_beta"],
            lim1=options["ctf_lim1"],
            lim2=options["ctf_lim2"],
            logger=self.logger
        )


    @pipeline_step("phase_retrieval", "Performing phase retrieval")
    def _retrieve_phase_ctf(self):
        options = self.processing_options["phase"]
        padding_mode = options["padding_type"]
        for i in range(self.radios.shape[0]):
            self.phase_retrieval.retrieve_phase(
                self.radios[i],
                output=self.radios[i],
                normalize_by_mean=options["ctf_normalize_by_mean"],
            )


    def _read_data(self):
        super()._read_data()
        self._d_radios.set(self.radios)
        self._h_radios = self.radios
        self.radios = self._d_radios

    def _write_data(self, data=None):
        self._d_radios.get(ary=self._h_radios)
        self.radios = self._h_radios
        super()._write_data(data=self.radios)



class CudaSinoStackPipeline(SinoStackPipeline):
    backend = "cuda"
    SinoBuilderClass = SinoBuilder # done on host to save device memory
    SinoNormalizationClass = CudaSinoNormalization
    SinoDeringerClass = CudaMunchDeringer
    FBPClass = Backprojector
    HistogramClass = CudaPartialHistogram

    def __init__(self, process_config, stack, projections, logger=None, extra_options=None, cuda_options=None):
        self._init_cuda(cuda_options)
        super().__init__(
             process_config, stack, projections, logger=logger, extra_options=extra_options,
        )

    # TODO base class ?
    _init_cuda = CudaGroupedPipeline._init_cuda
    _allocate_array = CudaChunkedPipeline._allocate_array
    _allocate_array_on_host = GroupedPipeline._allocate_array

    def _allocate_sinobuilder_output(self):
        # build_sino is done on host. Use host allocation
        return self._allocate_array_on_host(self.sino_builder.output_shape, "f", name="sinos")

    def _build_sino(self):
        super()._build_sino()
        self._allocate_array(self.sino_builder.output_shape, "f", name="sinos")
        self._d_sinos.set(np.ascontiguousarray(self.sinos)) # !
        self._h_sinos = self.sinos
        self.sinos = self._d_sinos


    def _write_data(self, data=None):
        recs = self._d_recs.get() # not ideal - use self.recs ?
        super()._write_data(data=recs)
