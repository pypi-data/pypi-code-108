# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Safe resource limits class for early termination.

Implementation of resource limits with fallback for systems
which do not support the python resource module.
"""
from typing import Any, Callable, Dict, Optional, Tuple, Union
import logging
import os
import sys
import time

from .limit_function_call_spawn import EnforceLimits
from .types import T


logger = logging.getLogger(__name__)

SIMPLE_PLATFORMS = {
    'linux': 'linux',
    'linux2': 'linux',
    'darwin': 'osx',
    'win32': 'win'
}

simple_platform = SIMPLE_PLATFORMS.get(sys.platform, 'unknown')

TIME_CONSTRAINT = 'wall_time_in_s'
TOTAL_TIME_CONSTRAINT = 'total_wall_time_in_s'
MEM_CONSTRAINT = 'mem_in_mb'
_ONE_WEEK_IN_SECONDS = 60 * 60 * 24 * 7
_TOTAL_TIME_MULTIPLIER = 52

DEFAULT_RESOURCE_LIMITS = {
    # note that this is approximate
    MEM_CONSTRAINT: None,
    # Use 1 week time out so that we dont interfere with user specified timeout
    # and dont cause errors for being too big
    TIME_CONSTRAINT: _ONE_WEEK_IN_SECONDS,
    # Use 1 year time out so that we dont interfere with user specified timeout.
    TOTAL_TIME_CONSTRAINT: _ONE_WEEK_IN_SECONDS * _TOTAL_TIME_MULTIPLIER,
    'cpu_time_in_s': None,
    'num_processes': None,
    'grace_period_in_s': None
}


# use this for module functions
class SafeEnforceLimits:
    """Class to allow for early termination of an execution."""

    def get_param_str(self, params: Dict[str, Any]) -> str:
        """
        Combine the key-value in kwargs as a string.

        :param params:
        :return: str.
        """
        s = ""
        for k, v in params.items():
            s += k + "=" + str(v) + ", "
        return s

    def __init__(self,
                 enable_limiting: bool = True,
                 **kwargs: Any):
        """
        Init the class.

        :param args:
        :param kwargs:
        """
        if enable_limiting:
            self.limiter = EnforceLimits(**kwargs)     # type: Optional[EnforceLimits]
            logger.info("Limits set to %s" % self.get_param_str(kwargs))
        else:
            logger.info('Limiting disabled.')
            self.limiter = None

    def wrap(self,
             func: 'Callable[..., T]',
             working_dir: str) -> 'Callable[..., Tuple[Optional[T], Optional[BaseException], float]]':
        """
        Wrap a function to limit its resource usage.

        :param func:
        :param working_dir:
        :return:
        """
        def wrapped(*args: Any, **kwargs: Any) -> Tuple[Optional[T], Optional[BaseException], float]:
            # capture and log stdout, stderr
            # out, err = sys.stdout, sys.stderr
            # out_str, err_str = StringIO(), StringIO()
            # sys.stdout, sys.stderr = out_str, err_str

            result, exit_status, wall_clock_time = None, None, 0.0

            if self.limiter is not None:
                result, exit_status, wall_clock_time = self.limiter.execute(working_dir, func, *args, **kwargs)
            else:
                start = time.time()
                try:
                    # We need to remove cache_store key as it is only required by the subprocess (limiter).
                    # Task 1202099 - remove AutoML specific code from resource limits and spawn proc.
                    if "cache_store" in kwargs:
                        kwargs.pop("cache_store")
                    result = func(*args, **kwargs)
                except Exception as e:
                    exit_status = e
                finally:
                    wall_clock_time = time.time() - start

            # out_str, err_str = out_str.getvalue(), err_str.getvalue()
            # if err_str != "": self.log.error(err_str)
            # if out_str != "": self.log.info(out_str)
            # sys.stdout, sys.stderr = out, err

            return result, exit_status, wall_clock_time
        return wrapped

    def execute(self,
                working_dir: str,
                func: 'Callable[..., T]',
                *args: Any,
                **kwargs: Any) -> Tuple[Optional[T], Optional[BaseException], float]:
        """
        Execute function with limits.

        :param working_dir:
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        wrapped_func = self.wrap(func, working_dir)
        return wrapped_func(*args, **kwargs)
