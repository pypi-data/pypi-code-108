# Copyright IBM Corp. 2021. All Rights Reserved.

import sys

from .client import WSPipelines
from .cpd_paths import CpdScope, CpdPath
from .version import __version__

if sys.version_info[0] == 2:
    import logging

    logger = logging.getLogger('ibm_watson_studio_pipelines_initialization')
    logger.warning("Python 2 is not supported.")