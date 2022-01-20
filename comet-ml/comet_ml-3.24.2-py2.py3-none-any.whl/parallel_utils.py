# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed
#  without the express permission of Comet ML Inc.
# *******************************************************
import logging
import multiprocessing.pool
import os
import threading
from functools import wraps

from ._typing import Callable, Tuple

LOGGER = logging.getLogger(__name__)


def get_thread_pool(worker_cpu_ratio):
    # type: (int) -> Tuple[int, int, multiprocessing.pool.ThreadPool]

    # Use the same max size than concurrent.futures.ThreadPoolExecutor which we should use once
    # Python 2.7 is not supported

    if not isinstance(worker_cpu_ratio, int) or worker_cpu_ratio <= 0:
        LOGGER.debug("Invalid worker_cpu_ratio %r", worker_cpu_ratio)
        worker_cpu_ratio = 4

    cpu_count = multiprocessing.cpu_count() or 1
    pool_size = min(64, cpu_count * worker_cpu_ratio)

    return (pool_size, cpu_count, multiprocessing.pool.ThreadPool(processes=pool_size))


def synchronised(func):
    # type: (Callable) -> Callable
    """The decorator to make particular function synchronized"""
    func.__lock__ = threading.Lock()  # type: ignore

    @wraps(func)
    def synced_func(*args, **kws):
        with func.__lock__:  # type: ignore
            return func(*args, **kws)

    return synced_func


@synchronised
def makedirs_synchronized(name, exist_ok=False):
    """
    Replacement for Python2's version lacking exist_ok
    """
    if not os.path.exists(name) or not exist_ok:
        os.makedirs(name)
