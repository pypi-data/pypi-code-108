from .trial_metadata import *
from .file_metadata import *
from .assay_metadata import *

# Everything has to be imported after the tables they reference
from .assay_templates import *
from .manifest_templates import *
from .sync_schemas import *

from .model_core import *
from .core import *
from .utils import *

# This maps from full_template_name prism/CLI-compatible
# assay names to the MetadataTemplate instances that
# handles each type of upload.
TEMPLATE_MAP = {
    get_full_template_name(name): value
    for name, value in dict(globals(), **locals()).items()
    if isinstance(value, MetadataTemplate)
}
