import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum

from typing import Optional, List, Union, Dict

from stringcase import camelcase

from dataclass_dict_convert import dataclass_dict_convert, dataclass_copy_method, dataclass_auto_type_check


# 2 seperate usage statistics:
#   "cpu" -> CpuUsageStatistics -> not just CPU, but everything but GPU -> reported by docker etc
#   "gpu"  -> GPUUsageStatistics -> GPU -> reported by nv libraries
# Combined in GPULabUsageStatistics

@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class ContainerUsageStatistics:
    first_time: datetime.datetime
    last_time: datetime.datetime
    agg_period_ns: int
    cpu_count: int
    cpu_usage: float  # in nr CPU's, so between 0 and cpu_count
    cpu_usage_total_ns: int
    cpu_usage_kernelmode_ns: int
    cpu_usage_usermode_ns: int
    max_pid_count: int
    mem_limit_byte: int
    mem_max_usage_byte: int
    network_rx_byte: int
    network_tx_byte: int

    def is_invalid(self):
        return self.agg_period_ns <= 0 \
               or self.cpu_count <= 0 \
               or self.first_time <= datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    def to_timeseriesdb_entry(self) -> dict:
        return {
            'sample_period_ns': self.agg_period_ns,
            'pid_count': self.max_pid_count,
            'cpu_usage_total_ns': self.cpu_usage_total_ns,
            'cpu_usage_kernelmode_ns': self.cpu_usage_kernelmode_ns,
            'cpu_usage_usermode_ns': self.cpu_usage_usermode_ns,
            'mem_usage_byte': self.mem_max_usage_byte,
            'mem_limit_byte': self.mem_limit_byte,
            'cpu_usage': self.cpu_usage,
            'cpu_usage_percent_all': ((self.cpu_usage * 100.0) / self.cpu_count) if self.cpu_count > 0 else -1,  # float
            'cpu_count': self.cpu_count,
            'network_rx_byte': self.network_rx_byte,
            'network_tx_byte': self.network_tx_byte,
        }

    @classmethod
    def invalid(cls):
        return ContainerUsageStatistics(
            first_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            last_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            agg_period_ns=-1,
            cpu_count=-1,
            cpu_usage=-1.0,
            cpu_usage_total_ns=-1,
            cpu_usage_kernelmode_ns=-1,
            cpu_usage_usermode_ns=-1,
            max_pid_count=-1,
            mem_limit_byte=-1,
            mem_max_usage_byte=-1,
            network_rx_byte=-1,
            network_tx_byte=-1,
        )


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuUsageStatistics:
    gpu_count: int
    average_utilization: float  # in number of GPU's, so between 0 and gpu_count
    average_mem_utilization: float  # in number of GPU's, so between 0 and gpu_count

    @classmethod
    def empty(cls):
        return GpuUsageStatistics(0, 0.0, 0.0)


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GPULabUsageStatistics:
    container_statistics: ContainerUsageStatistics
    gpu_statistics: GpuUsageStatistics


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuInfo:
    index: int
    uuid: str
    serial: str
    name: str
    brand: str
    minor_number: int
    board_id: int
    bridge_chip_info: str
    is_multi_gpu_board: bool
    max_pcie_link_generation: int
    max_pcie_link_width: int
    vbios_version: str

# example:
#               board_id: 768,
#               brand: "GeForce",
#               bridge_chip_info: "N/A",
#               index: 0,
#               is_multi_gpu_board: false,
#               max_pcie_link_generation: 3,
#               max_pcie_link_width: 16,
#               minor_number: 0,
#               name: "GeForce GTX 980",
#               serial: "N/A",
#               uuid: "GPU-8a56a4bc-e184-a047-2620-be19fdf913d5",
#               vbios_version: "84.04.31.00.29"


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    direct_fields=['cuda_version_minor'],
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuOverview:
    cuda_version_full: str  # from resource manager
    cuda_version_int: int  # from nv utils
    cuda_version_major: int
    cuda_version_minor: Union[int, float]
    driver_version: str
    nvml_version: str
    gpus: List[GpuInfo]

# Example:
#     cuda_driver_version_full: "10.2.0",
#     cuda_driver_version_int: 10020,
#     cuda_driver_version_major: 10,
#     cuda_driver_version_minor: 2, // or 2.0 !
#     driver_version: "440.33.01",
#     nvml_version: "10.440.33.01",
#     gpu: [...]
