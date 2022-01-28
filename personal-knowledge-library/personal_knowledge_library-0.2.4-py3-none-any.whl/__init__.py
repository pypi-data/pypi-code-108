# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.

import logging
from typing import Optional

__author__ = "Markus Weber"
__copyright__ = "Copyright 2021 Wacom. All rights reserved."
__credits__ = ["Markus Weber"]
__license__ = "Wacom"
__maintainer__ = ["Markus Weber"]
__email__ = "markus.weber@wacom.com"
__status__ = "beta"

# Create the Logger
logger: Optional[logging.Logger] = None

if logger is None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch: logging.StreamHandler = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

__all__ = ['__copyright__', '__credits__', '__license__', '__maintainer__', '__email__', '__status__',
           'logger', 'base', 'nel', 'public', 'services', 'utils']

from knowledge import base
from knowledge import nel
from knowledge import public
from knowledge import services
from knowledge import utils
