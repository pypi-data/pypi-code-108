import sys

from loguru import logger
import sentry_sdk

from .config import *


from .project import Project, login
from .core.compiler.onnc_saas import ONNCSaaSBuilder
from .config import api_protocol, api_url, api_port

# from .workspace import *
# from .workspacev2 import CompressFormt, ModelFormat, SampleFormat, SampleSource
# from .workspacev2 import Samples, launch

# logger.remove(0)
# logger.start(sys.stdout, colorize=True, format="<level>{level}</level> {message}")

sentry_sdk.init(
    "https://da9cdf5759874504940714a91657de21@o304393.ingest.sentry.io/5901378",
    traces_sample_rate=1.0
)
fpath = os.path.dirname(os.path.abspath(__file__))

__version__= "2.3.0"

