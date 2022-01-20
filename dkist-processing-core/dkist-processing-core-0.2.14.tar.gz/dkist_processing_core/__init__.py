from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

from dkist_processing_core.task import TaskBase
from dkist_processing_core.workflow import Workflow

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"
