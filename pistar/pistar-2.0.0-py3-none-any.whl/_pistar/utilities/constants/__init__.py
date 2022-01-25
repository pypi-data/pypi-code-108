"""
description: this module provides constants.
"""

import os

from _pistar.utilities.constants.testcase import ControlArgs
from .action_word import ACTION_WORD_KEYS
from .action_word import ACTION_WORD_STATUS
from .encode import ENCODE
from .file_mode import FILE_MODE
from .pistar_logging import LOGGING_FORMAT
from .pistar_logging import LOGGING_HANDLER
from .pistar_logging import LOGGING_LEVEL
from .report import REPORT_TYPE
from .testcase import PISTAR_TESTCASE_EXECUTION_STATUS
from .testcase import STEP_TYPE
from .testcase import TESTCASE_EXECUTION_STATUS
from .testcase import TESTCASE_KEYS
from .testcase import TESTCASE_PROPERTIES
from .testcase import TESTCASE_STATUS
from .yaml_type import YAML_TYPE
from .generate import GENERATE_KEYS

ROOT_CONFIGURATION_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', '_pistar', 'configuration.yaml')
