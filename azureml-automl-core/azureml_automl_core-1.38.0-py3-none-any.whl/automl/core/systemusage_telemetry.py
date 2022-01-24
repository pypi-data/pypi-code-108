# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""systemusage_telemetry.py, A file system usage telemetry classes."""
import abc
import logging
import os
import sys
from typing import Optional, Tuple

from .timer_utilities import TimerCallback


logger = logging.getLogger(__name__)


class SystemResourceUsageTelemetry:
    """System usage telemetry abstract class."""

    def __init__(self, interval=10):
        """
        Initialize system resource usage telemetry class.

        :param interval: interval in sec
        """
        self.interval = interval
        self._timer = None
        self._max_mem = None

    def __enter__(self):
        """Start usage collection using a context manager."""
        self._max_mem = 0
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop usage collection using a context manager."""
        self.stop()

    def start(self):
        """Start usage collection."""
        if self._timer is None:
            logger.info("Starting usage telemetry collection")
            self._timer = TimerCallback(interval=self.interval, callback=self._get_usage)
            self._timer.start()

    def stop(self):
        """Stop timer."""
        if self._timer is not None:
            logger.info("Stopping usage telemetry collection")
            self._timer.stop()
            self._timer = None

    def __del__(self):
        """Cleanup."""
        self.stop()

    def _log_memory_usage(self, mem_usage, prefix_message=""):
        """Log memory usage."""
        extra_info = {"properties": {"Type": "MemoryUsage", "Usage": mem_usage}}
        if prefix_message is None:
            prefix_message = ""
        logger.info("{}memory usage {}".format(prefix_message, mem_usage), extra=extra_info)

    def _log_cpu_usage(self, cpu_time, cores, system_time=None, prefix_message=""):
        """Log cpu usage."""
        extra_info = {"properties": {"Type": "CPUUsage", "CPUTime": cpu_time, "Cores": cores}}
        if system_time is not None:
            extra_info["properties"]["SystemTime"] = system_time
        if prefix_message is None:
            prefix_message = ""
        logger.info("{}cpu time {}".format(prefix_message, cpu_time), extra=extra_info)

    def send_usage_telemetry_log(self, prefix_message=None):
        """
        Send the usage telemetry log based on automl settings with message.

        :param prefix_message: The prefix of logging message.
        :return: None
        """
        try:
            self._get_usage(prefix_message)
        except Exception:
            pass  # do nothing

    @abc.abstractmethod
    def _get_usage(self, prefix_message=None):
        raise NotImplementedError

    def _get_psutil_mem_stats(self) -> Tuple[Optional[int], Optional[int]]:
        try:
            import psutil

            current_process = psutil.Process(os.getpid())
            parent_mem = current_process.memory_full_info().rss
            child_mem = parent_mem
            for child in current_process.children(recursive=True):
                child_mem += child.memory_full_info().rss
            return parent_mem, child_mem
        except Exception:
            return None, None


class _WindowsSystemResourceUsageTelemetry(SystemResourceUsageTelemetry):
    """Telemetry Class for collecting system usage."""

    def __init__(self, interval=10):
        """
        Constructor.

        :param interval: collection frequency in seconds
        """
        super(_WindowsSystemResourceUsageTelemetry, self).__init__(interval=interval)

    def _get_usage(self, prefix_message=None):
        """Get usage."""
        if prefix_message is None:
            prefix_message = ""

        try:
            from azureml.automl.runtime.shared.win32_helper import Win32Helper

            phys_mem, _, kernel_cpu, user_cpu, child_phys_mem, _, child_kernel_cpu, child_user_cpu = (
                Win32Helper.get_resource_usage()
            )

            # Get memory stats from psutil
            psutil_parent_mem, psutil_child_mem = self._get_psutil_mem_stats()

            if psutil_parent_mem is not None:
                phys_mem = psutil_parent_mem
            if psutil_child_mem is not None:
                child_phys_mem = psutil_child_mem

            self._log_memory_usage(phys_mem, prefix_message)
            self._log_memory_usage(child_phys_mem, "{}child ".format(prefix_message))

            self._log_cpu_usage(user_cpu, os.cpu_count(), kernel_cpu, prefix_message)
            self._log_cpu_usage(child_user_cpu, os.cpu_count(), child_kernel_cpu, "{}child ".format(prefix_message))
        except Exception:
            logger.info("Unable to obtain memory usage.")


class _NonWindowsSystemResourceUsageTelemetry(SystemResourceUsageTelemetry):
    """Linux, Mac & other os System Usage Telemetry."""

    def _get_usage(self, prefix_message=None):
        """Get usage."""
        if prefix_message is None:
            prefix_message = ""

        try:
            import resource

            res = resource.getrusage(resource.RUSAGE_SELF)
            child_res = resource.getrusage(resource.RUSAGE_CHILDREN)

            # Get memory stats from psutil
            psutil_parent_mem, psutil_child_mem = self._get_psutil_mem_stats()

            if psutil_parent_mem is not None:
                mem = psutil_parent_mem
                child_mem = psutil_child_mem
            else:
                mem = res.ru_maxrss
                child_mem = child_res.ru_maxrss

            self._log_memory_usage(mem, prefix_message)
            self._log_memory_usage(child_mem, "{}child ".format(prefix_message))

            self._log_cpu_usage(res.ru_utime, os.cpu_count(), res.ru_stime, prefix_message)
            self._log_cpu_usage(
                child_res.ru_utime, os.cpu_count(), child_res.ru_stime, "{}child ".format(prefix_message)
            )
        except Exception:
            logger.info("Unable to obtain memory usage.")


class SystemResourceUsageTelemetryFactory:
    """System resource usage telemetry collection factory class."""

    @staticmethod
    def get_system_usage_telemetry(interval: int = 10) -> SystemResourceUsageTelemetry:
        """
        Get system usage telemetry object based on platform.

        :param interval: interval in sec
        :return: SystemResourceUsageTelemetry : platform specific object
        """
        if sys.platform == "win32":
            return _WindowsSystemResourceUsageTelemetry(interval=interval)

        return _NonWindowsSystemResourceUsageTelemetry(interval=interval)


_system_usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry()
