# Copyright 2019 StreamSets Inc.

import logging
import os

from .accounts import Accounts
from .config import USER_CONFIG_PATH, ACTIVATION_KEY_ENV_VAR_NAME
from .sdc import DataCollector
from .sch import ControlHub
from .st import Transformer

__all__ = ['Accounts', 'ControlHub', 'DataCollector', 'Transformer']

__version__ = '3.12.dev2'

logger = logging.getLogger(__name__)

activation_path = os.path.join(USER_CONFIG_PATH, 'activation')

if not os.path.exists(activation_path) and not os.environ.get(ACTIVATION_KEY_ENV_VAR_NAME):
    logger.info('Creating user configuration directory at %s ...', USER_CONFIG_PATH)
    os.makedirs(activation_path)
