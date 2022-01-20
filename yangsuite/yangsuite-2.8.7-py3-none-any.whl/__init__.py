# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""YANG-Suite application package."""

import logging

from .logs import get_logger
from .paths import get_path, register_path
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

default_app_config = 'yangsuite.apps._YangsuiteConfig'

__all__ = (
    'get_logger',
    'get_path',
    'register_path',
)

# Create logger for module and set defaults
# Django may override this in settings.py
logger = logging.getLogger('yangsuite')

logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s: %(levelname)s: %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)
