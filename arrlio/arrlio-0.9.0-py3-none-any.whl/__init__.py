import logging
import sys


log_frmt = logging.Formatter("%(asctime)s %(levelname)s [arrlio] %(message)s")
log_hndl = logging.StreamHandler(stream=sys.stderr)
log_hndl.setFormatter(log_frmt)
logger = logging.getLogger("arrlio")
logger.addHandler(log_hndl)
logger.setLevel("INFO")


__version__ = "0.9.0"

__tasks__ = {}


from arrlio.core import App, logger, task  # noqa
from arrlio.exc import NotFoundError, TaskError, TaskNoResultError, TaskTimeoutError  # noqa
from arrlio.models import Graph  # noqa
from arrlio.settings import Config  # noqa
