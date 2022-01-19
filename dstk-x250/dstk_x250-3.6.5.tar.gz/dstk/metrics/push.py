#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outils associés à la gestion des métriques

Created on Sun Nov 22 12:32:15 2020

@author: Cyrile Delestre
"""

import logging
from typing import Any, Dict

def _push_logger(logger: logging.Logger, message: Dict[str, Any]):
    r"""
    Fonction privée de push vers un logger. Si None print le résultat.
    """
    if logger is None:
        print(message, flush=True)
    elif isinstance(logger, logging.Logger):
        logger.info(message)
    elif isinstance(logger, list):
        logger.append(message)