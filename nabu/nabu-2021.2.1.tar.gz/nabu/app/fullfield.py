from ..pipeline.fullfield.chunked import ChunkedPipeline as FullFieldPipeline
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.resources.app.fullfield was moved to nabu.pipeline.fullfield.chunked.",
    func_name="fullfield_pipeline"
)