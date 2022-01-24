from ..pipeline.fullfield.grouped import GroupedPipeline as FullRadiosPipeline, SinoStackPipeline
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.resources.app.fullfield_mixed was moved to nabu.pipeline.fullfield.grouped.",
    func_name="fullfield_mixed_reconstruction"
)