# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""SystemMeter class."""

import psutil
import pynvml
import torch

from typing import Any, Dict

from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common import distributed_utils
from azureml.automl.dnn.vision.common.logging_utils import get_logger

MEGABYTE = 1024.0 * 1024.0

logger = get_logger(__name__)


class SystemMeter:
    """Collects and logs system and gpu metrics like memory and percent of utilization.
       In distributed mode, logging and collection of stats is no-op on non-master processes."""

    GPU_MEM_KEY = "mem_info_used"
    GPU_USAGE_KEY = "gpu_utilization"
    PERCENT = "percent"
    USED = "used"
    SHARED = "shared"

    MEMORY_METERS = {SHARED, USED, PERCENT}
    MEMORY_METERS_MB = {SHARED, USED}

    def __init__(self, log_processes_info: bool = False,
                 log_static_sys_info: bool = False) -> None:
        """Resets accumulators.

        :param log_processes_info: if True, details about all running processes are logged.
                                   They are only logged once per instance of the meter.
        :type log_processes_info: bool
        :param log_static_sys_info: if True, static system properties (like disk partitions) are logged.
        :type log_static_sys_info: bool
        """

        self.log_static_sys_info = log_static_sys_info
        self.show_processes = log_processes_info

        # used to accumulate gpu usage values over time.
        self.gpu_mem_usage_accumulator: Dict[Any, Any] = {}
        self.gpu_usage_accumulator: Dict[Any, Any] = {}

        # used to accumulate system stats value over time.
        self.sys_mem_usage_accumulator: Dict[Any, Any] = {}

        self.master_process = distributed_utils.master_process()

    def reset_sys_stats(self) -> None:
        """Resets system stats accumulator."""
        self.sys_mem_usage_accumulator = {}

    def reset_gpu_stats(self) -> None:
        """Resets gpu stats accumulator."""
        self.gpu_mem_usage_accumulator = {}
        self.gpu_usage_accumulator = {}

    def reset(self) -> None:
        """Resets system and gpu stats accumulator."""
        self.reset_gpu_stats()
        self.reset_sys_stats()

    def get_avg_mem_stats(self) -> str:
        """Returns a string representation of CPU memory avg utilization."""
        return str(self.sys_mem_usage_accumulator) if self.master_process else ""

    def get_avg_gpu_stats(self) -> str:
        """Returns a string representation of gpu avg utilization."""
        return str(self.gpu_mem_usage_accumulator) + str(self.gpu_usage_accumulator) if self.master_process else ""

    def _get_mem_stats(self) -> str:
        """Computes and returns a string with CPU memory usage.

        :return: a string with CPU memory usage.
        :rtype String
        """

        mem = psutil.virtual_memory()
        mem_dict = mem._asdict()
        if self.sys_mem_usage_accumulator is not None:
            for k in self.MEMORY_METERS:
                if k not in self.sys_mem_usage_accumulator:
                    self.sys_mem_usage_accumulator[k] = AverageMeter()
                if k in mem_dict:
                    value = mem_dict[k]
                    if k in self.MEMORY_METERS_MB:
                        value /= MEGABYTE
                    self.sys_mem_usage_accumulator[k].update(value)

        mem_dict = self._to_mb(mem_dict)
        mem_str = str(dict(mem_dict))
        return mem_str

    def _get_gpu_stats(self) -> str:
        """Computes and returns a string with GPU usage.

        :return: a string with GPU usage.
        :rtype String
        """

        if not self.master_process:
            return ""

        if not torch.cuda.is_available():
            return "<none>"

        pynvml.nvmlInit()
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            usage_str = ""
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization_rates = pynvml.nvmlDeviceGetUtilizationRates(handle)

                mem_total = "{0:.2f}".format(mem_info.total / MEGABYTE)
                mem_free = "{0:.2f}".format(mem_info.free / MEGABYTE)
                mem_used = "{0:.2f}".format(mem_info.used / MEGABYTE)
                usage_str += "{}:  Mem (MB): mem_info_total={}, mem_info_free={}, mem_info_used={}, " \
                             "gpu_utilization={}%".format(pynvml.nvmlDeviceGetName(handle),
                                                          mem_total, mem_free, mem_used,
                                                          utilization_rates.gpu)
                if self.gpu_mem_usage_accumulator is not None:
                    self.gpu_mem_usage_accumulator[i] = self.gpu_mem_usage_accumulator.get(i, {})
                    if self.GPU_MEM_KEY not in self.gpu_mem_usage_accumulator[i]:
                        self.gpu_mem_usage_accumulator[i][self.GPU_MEM_KEY] = AverageMeter()
                    self.gpu_mem_usage_accumulator[i][self.GPU_MEM_KEY].update(mem_info.used / MEGABYTE)
                    usage_str += ", avg_mem_info_used={0:.2f} ".format(
                        self.gpu_mem_usage_accumulator[i][self.GPU_MEM_KEY].avg)
                if self.gpu_usage_accumulator is not None:
                    self.gpu_usage_accumulator[i] = self.gpu_usage_accumulator.get(i, {})
                    if self.GPU_USAGE_KEY not in self.gpu_usage_accumulator[i]:
                        self.gpu_usage_accumulator[i][self.GPU_USAGE_KEY] = AverageMeter()
                    self.gpu_usage_accumulator[i][self.GPU_USAGE_KEY].update(utilization_rates.gpu)
                    usage_str += ", avg_gpu_utilization={}% ".format(
                        self.gpu_usage_accumulator[i][self.GPU_USAGE_KEY].avg)

            return usage_str if usage_str else "<none>"
        except pynvml.NVMLError as error:
            error_str = str(error)
            return error_str if error_str else "<none>"
        finally:
            pynvml.nvmlShutdown()

    def _to_mb(self, dict_to_convert: Dict[str, str]) -> Dict[str, str]:
        """Converts some of the elements in the dictionary in MB.

        :param dict_to_convert: dictionary to convert
        :type dict_to_convert: dict
        :return converted dictionary
        :rtype dict
        """

        if not isinstance(dict_to_convert, dict):
            return dict_to_convert

        keys_to_convert = {"total", "used", "free", "available", "active",
                           "inactive", "buffers", "cached", "shared", "slab"}
        for k, v in dict_to_convert.items():
            if isinstance(v, dict):
                dict_to_convert[k] = self._to_mb(v)
            if k in keys_to_convert:
                dict_to_convert[k] = "{0:.2f}MB".format(int(dict_to_convert[k]) / MEGABYTE)

        return dict_to_convert

    def log_system_stats(self) -> None:
        """Logs system statistics like memory, disk and processes.

        :return:
        """

        if not self.master_process:
            return

        if self.log_static_sys_info:
            self.log_static_sys_info = False

            try:
                # cpu
                logger.info("Available vCPUs: {0}".format(psutil.cpu_count()))
            except Exception as e:
                logger.info("Exception while getting the vCPUs. {0}".format(e))

            try:
                # disk

                # List of named tuples containing all mounted disk partitions
                # Not logging for now as it may contain user data
                # dparts = psutil.disk_partitions()
                # logger.info("Disk Partitions = {0}".format(dparts))

                # Disk and shared memory usage statistics
                du = psutil.disk_usage('/')
                logger.info("Disk Usage  ('/') = {0}".format(dict(self._to_mb(du._asdict()))))
                du = psutil.disk_usage('/dev/shm')
                logger.info("Shared Memory Usage ('/dev/shm') = {0}".format(dict(self._to_mb(du._asdict()))))
            except Exception as e:
                logger.info("Exception while getting the disk stats. {0}".format(e))

        try:
            # system memory and gpu+gpu memory usage statistics
            mem_stats = self._get_mem_stats()
            logger.info("Virtual Memory = {0}".format(mem_stats))
            gpu_stats = self._get_gpu_stats()
            logger.info("GPU = {0}\n".format(gpu_stats))

        except Exception as e:
            logger.info("Exception while getting the mem and gpu stats. {0}".format(e))

        if self.show_processes:
            try:
                # processes

                # List of current running process IDs.
                pids = psutil.pids()
                logger.info("psutil.pids() = {0}".format(pids))

                # Check whether the given PID exists in the current process list.
                for process in psutil.process_iter():
                    try:
                        process_info = self._to_mb(process.as_dict(attrs=['pid', 'name', 'exe', 'memory_info']))
                    except psutil.NoSuchProcess:
                        pass
                    else:
                        logger.info(process_info)
            except Exception as e:
                logger.info("Exception while getting the processes stats. {0}".format(e))
