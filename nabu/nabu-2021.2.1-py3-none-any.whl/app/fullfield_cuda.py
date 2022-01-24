from ..pipeline.fullfield.chunked_cuda import CudaChunkedPipeline as CudaFullFieldPipeline, CudaChunkedPipelineLimitedMemory as CudaFullFieldPipelineLimitedMemory
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.resources.app.fullfield_cuda was moved to nabu.pipeline.fullfield.chunked_cuda.",
    func_name="fullfield_cuda_pipeline"
)