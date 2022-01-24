# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Limit function calls using spawn.

Limit function calls to specified resource constraints, but guarantees
the use of "spawn" instead of "fork" in order to be compatible with
libraries that aren't fork-safe (e.g. LightGBM).

Adapted from https://github.com/sfalkner/pynisher
"""
from typing import Any, Callable, Optional, Tuple, Union
import errno
import os
import logging
import subprocess
import time

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory, IterationTimedOut
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import MemorylimitException, ResourceException
from azureml.automl.core.shared.limit_function_call_exceptions import (
    CpuTimeoutException,
    TimeoutException,
    SubprocessException,
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared import limit_function_call_limits, spawn_client
from azureml.automl.runtime.shared.types import T

logger = logging.getLogger(__name__)


class EnforceLimits:
    """Base class to enforce resource limits."""

    def __init__(
        self,
        mem_in_mb: Optional[int] = None,
        cpu_time_in_s: Optional[int] = None,
        wall_time_in_s: Optional[int] = None,
        num_processes: Optional[int] = None,
        grace_period_in_s: Optional[int] = None,
        total_wall_time_in_s: Optional[int] = None
    ) -> None:
        """
        Resource limit to be enforced.

        :param mem_in_mb:
        :param cpu_time_in_s:
        :param wall_time_in_s:
        :param num_processes:
        :param grace_period_in_s:
        :param total_wall_time_in_s: unused now but used to limit the entire run
        """
        self.mem_in_mb = mem_in_mb
        self.cpu_time_in_s = cpu_time_in_s
        self.num_processes = num_processes

        if total_wall_time_in_s is None:
            self.wall_time_in_s = wall_time_in_s
        elif wall_time_in_s is None:
            self.wall_time_in_s = total_wall_time_in_s
        else:
            self.wall_time_in_s = min(wall_time_in_s, total_wall_time_in_s)

        self.grace_period_in_s = 0 if grace_period_in_s is None else grace_period_in_s

        if self.mem_in_mb is not None:
            logger.debug("Restricting your function to {} mb memory.".format(self.mem_in_mb))
        if self.cpu_time_in_s is not None:
            logger.debug("Restricting your function to {} seconds cpu time.".format(self.cpu_time_in_s))
        if self.wall_time_in_s is not None:
            logger.debug("Restricting your function to {} seconds wall time.".format(self.wall_time_in_s))
        if self.num_processes is not None:
            logger.debug("Restricting your function to {} threads/processes.".format(self.num_processes))
        if self.grace_period_in_s is not None:
            logger.debug("Allowing a grace period of {} seconds.".format(self.grace_period_in_s))

    def execute(
        self, working_dir: str, func: "Callable[..., T]", *args: Any, **kwargs: Any
    ) -> Tuple[Optional[T], Optional[BaseException], float]:
        """
        Execute the function with the resource constraints applied.

        :param working_dir: the working directory to use for temporary files
        :param func: the function to execute
        :param args: list of positional args to pass to the function
        :param kwargs: list of keyword args to pass to the function
        :return: a value/error/execution time tuple
        """
        result = None
        exit_status = None  # type: Optional[BaseException]

        # Only log types to prevent possibility of leaking PII
        logger.info(
            "Calling function {} with argument types: {}, {}".format(
                func, [x.__class__ for x in args], {k: kwargs[k].__class__ for k in kwargs}
            )
        )

        # determine timeout
        timeout = None
        if self.wall_time_in_s is not None:
            timeout = self.wall_time_in_s + self.grace_period_in_s

        # create and start the process
        start = time.time()
        try:
            result = spawn_client.run_in_proc(
                working_dir,
                timeout,
                EnforceLimits.subprocess_func,
                args=(
                    func,
                    self.mem_in_mb,
                    self.cpu_time_in_s,
                    self.wall_time_in_s,
                    self.num_processes,
                    self.grace_period_in_s,
                ) + args,
                **kwargs,
            )
        except subprocess.TimeoutExpired:
            exit_status = TimeoutException._with_error(AzureMLError.create(IterationTimedOut))
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            exit_status = e
        finally:
            wall_clock_time = time.time() - start

        return result, exit_status, wall_clock_time

    @staticmethod
    def subprocess_func(
        func: "Callable[..., T]",
        mem_in_mb: Optional[int],
        cpu_time_limit_in_s: Optional[int],
        wall_time_limit_in_s: Optional[int],
        num_procs: Optional[int],
        grace_period_in_s: int,
        *args: Any,
        **kwargs: Any
    ) -> Tuple[Optional[T], Optional[BaseException]]:
        """
        Create the function the subprocess can execute.

        :param func: the function to enforce limit on
        :param mem_in_mb:
        :param cpu_time_limit_in_s:
        :param wall_time_limit_in_s:
        :param num_procs:
        :param grace_period_in_s:
        :param args: the args for the function
        :param kwargs: the kwargs for function
        :return:
        """
        limit_function_call_limits.set_limits(
            mem_in_mb, num_procs, wall_time_limit_in_s, cpu_time_limit_in_s, grace_period_in_s
        )

        try:
            logger.debug("call function")
            res = (func(*args, **kwargs), None)  # type: Tuple[Optional[T], Optional[BaseException]]
            logger.debug("function returned properly.")
        except CpuTimeoutException as e:
            res = (None, e)
        except TimeoutException as e:
            res = (None, e)
        except MemoryError as e:
            e = ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemory,
                    target=func.__qualname__,
                    reference_code=ReferenceCodes._OPERATION_FAILED_MEMORYERROR_SUBPROCESS,
                ),
                inner_exception=e,
            ).with_traceback(e.__traceback__)
            res = (None, e)
        except OSError as e:
            # errno and strerror do not expose PII
            msg = "[OSError {} ({})] {}".format(e.errno, errno.errorcode.get(e.errno, "Unknown"), os.strerror(e.errno))
            res = (None, SubprocessException.from_exception(e, msg))
        except Exception as e:
            res = (None, e)
            logging_utilities.log_traceback(e, logger)

        return res
