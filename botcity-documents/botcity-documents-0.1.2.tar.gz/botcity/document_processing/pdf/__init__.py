from .patch import patch_ltchar
# Patch to expose additional properties
patch_ltchar()

from .pdfreader import PDFReader  # noqa: F401, F403, E402
