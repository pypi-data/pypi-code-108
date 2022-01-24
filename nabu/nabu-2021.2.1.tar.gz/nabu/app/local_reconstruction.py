from ..pipeline.fullfield.local_reconstruction import ChunkedReconstructor, GroupedReconstructor
from ..utils import deprecation_warning

# Compat.
LocalReconstruction = ChunkedReconstructor
FullFieldReconstructor = ChunkedReconstructor
FullRadiosReconstructor = GroupedReconstructor
#

deprecation_warning(
    "nabu.resources.app.local_reconstruction was moved to nabu.pipeline.fullfield.local_reconstruction.",
    func_name="fullfield_local_reconstruction"
)