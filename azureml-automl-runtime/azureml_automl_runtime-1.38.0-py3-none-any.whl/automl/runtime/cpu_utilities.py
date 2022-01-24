# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility for getting CPU related information during AutoML training."""
from typing import Any, cast, Dict, Optional, Type
from types import TracebackType
import array
import csv
import functools
import platform
import sys

import psutil

from azureml.automl.core.timer_utilities import TimerCallback
from azureml.automl.runtime.shared.win32_helper import Win32Helper


def _get_num_physical_cpu_cores_model_explanations(max_cores_per_iteration: Optional[int] = None) -> int:
    """Return the number of CPU cores for explainable model for model explanations."""
    import psutil

    if max_cores_per_iteration is not None:
        return max_cores_per_iteration

    num_cpu_core = None
    try:
        num_cpu_core = psutil.cpu_count(logical=False)
    except Exception:
        # LightGBM doesn't perform as well if the number of jobs are set to available number
        # of logical cores. So approximating the number of cores to half of what is available.
        import os
        num_cpu_core = os.cpu_count()
        if num_cpu_core is not None:
            num_cpu_core /= 2

    if num_cpu_core is None:
        # Default to one cpu core if platform APIs don't return any value
        return 1
    else:
        return int(num_cpu_core)


def get_cpu_name() -> str:
    cpu_info = platform.processor()
    return cpu_info if cpu_info else 'Error getting CPU name'


@functools.lru_cache(maxsize=1)
def get_cpu_core_count(logical_core: Optional[bool] = False) -> int:
    return cast(int, psutil.cpu_count(logical=logical_core))


class ResourceUsageTracker:

    def __init__(self, output_file: Optional[str] = None) -> None:
        self._timer = None  # type: Optional[TimerCallback]
        self._peak_mem = 0
        self._starting_cpu_time = None  # type: Optional[float]
        self._starting_child_cpu_time = None  # type: Optional[float]
        self._current_cpu_time = 0  # type: float
        self._current_child_cpu_time = 0  # type: float

        self._output_file = output_file
        if self._output_file:
            # test to make sure this file can be opened
            with open(self._output_file, 'w'):
                pass

        self._cpu_times = array.array('d')        # type: array.array[float]
        self._child_cpu_times = array.array('d')  # type: array.array[float]
        self._memory_usage = array.array('Q')     # type: array.array[int]

    def __enter__(self) -> None:
        """Start resource monitoring using a context manager."""
        self._peak_mem = 0

        if sys.platform == "win32":
            callback = self._record_usage_win
        else:
            callback = self._record_usage_unix

        callback()
        self._starting_child_cpu_time = self._current_child_cpu_time
        self._starting_cpu_time = self._current_cpu_time

        self._timer = TimerCallback(interval=1, callback=callback)
        self._timer.start()

    def __exit__(self,
                 exc_type: 'Optional[Type[BaseException]]',
                 exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Stop resource monitoring using a context manager."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

        if self._output_file:
            # Dump all stats in CSV format if file specified
            with open(self._output_file, 'w', newline='') as csvfile:
                for mem, cpu, child_cpu in zip(self._memory_usage, self._cpu_times, self._child_cpu_times):
                    writer = csv.writer(csvfile)
                    writer.writerow((mem, cpu, child_cpu))

    @property
    def cpu_time(self) -> float:
        if self._starting_cpu_time is None:
            return 0
        return self._current_cpu_time - self._starting_cpu_time

    @property
    def child_cpu_time(self) -> float:
        if self._starting_child_cpu_time is None:
            return 0
        return self._current_child_cpu_time - self._starting_child_cpu_time

    @property
    def total_cpu_time(self) -> float:
        return self.cpu_time + self.child_cpu_time

    @property
    def peak_mem_usage(self) -> int:
        return self._peak_mem

    def _record_usage_unix(self) -> None:
        import resource
        res = resource.getrusage(resource.RUSAGE_SELF)
        child_res = resource.getrusage(resource.RUSAGE_CHILDREN)

        mem_usage = res.ru_maxrss + child_res.ru_maxrss
        if self._peak_mem < mem_usage:
            self._peak_mem = mem_usage

        self._current_cpu_time = (res.ru_utime + res.ru_stime)
        self._current_child_cpu_time = (child_res.ru_utime + res.ru_stime)

        if self._output_file:
            self._memory_usage.append(mem_usage)
            self._cpu_times.append(self._current_cpu_time)
            self._child_cpu_times.append(self._current_child_cpu_time)

    def _record_usage_win(self) -> None:
        phys_mem, _, kernel_cpu, user_cpu, child_phys_mem, _, child_kernel_cpu, child_user_cpu = \
            Win32Helper.get_resource_usage()

        mem_usage = phys_mem + child_phys_mem
        if self._peak_mem < mem_usage:
            self._peak_mem = mem_usage

        self._current_cpu_time = kernel_cpu + user_cpu
        self._current_child_cpu_time = child_kernel_cpu + child_user_cpu

        if self._output_file:
            self._memory_usage.append(mem_usage)
            self._cpu_times.append(self._current_cpu_time)
            self._child_cpu_times.append(self._current_child_cpu_time)

    def __del__(self) -> None:
        """Cleanup."""
        if self._timer is not None:
            self._timer.stop()
