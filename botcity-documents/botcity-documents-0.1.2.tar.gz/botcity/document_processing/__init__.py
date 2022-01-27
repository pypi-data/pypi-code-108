from .parser import Entry, DocumentParser  # noqa: F401, F403
from .pdf import PDFReader  # noqa: F401, F403

from botcity.document_processing._version import get_versions
__version__ = get_versions()['version']
del get_versions
