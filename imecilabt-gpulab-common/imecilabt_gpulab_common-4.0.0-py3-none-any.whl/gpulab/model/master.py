from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Union, List

from imecilabt.gpulab.model.job_filter2 import JobFilter2

from imecilabt.gpulab.model.usage_statistics import GPULabUsageStatistics, GpuOverview

from imecilabt.gpulab.model.job2 import JobStateResources as Job2StateResources, JobPortMapping as Job2PortMapping, \
    JobStatus as Job2Status, Job as Job2

from imecilabt.gpulab.model.slave_info2 import SlaveInfo2

from imecilabt.gpulab.model.job_filter import JobFilter

# Master: exposes all functionality of JobController, that is needed by the slave


class Master(ABC):
    @abstractmethod
    def find_jobs(self, job_filter: JobFilter2 = None, *, max_results: Optional[int] = 10, max_age_s: Optional[int] = 10 * 60) -> List[Job2]:
        pass

    @abstractmethod
    def update_job_status(self, job_id: str, target_job_state: Job2Status, *, onlyif_current_state: Optional[Job2Status] = None) -> None:
        pass

    @abstractmethod
    def init_job_state_resources(self, job_id: str, resources: Job2StateResources) -> None:
        pass

    @abstractmethod
    def init_job_state_resources_port_mapping(self, job_id: str, port_mappings: List[Job2PortMapping]) -> None:
        pass

    @abstractmethod
    def init_job_state_resources_gpu_details(self, job_id: str, gpu_details: GpuOverview) -> None:
        pass

    @abstractmethod
    def init_job_state_final_usage_statistics(self, job_id: str, final_usage_statistics: GPULabUsageStatistics) -> None:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Job2:
        pass

    @abstractmethod
    def append_to_log(self, job_id: str, extra_content: Union[bytes, str]) -> None:
        pass

    #Predefined logging levels are ints mapping to: CRITICAL, ERROR, WARNING, INFO, DEBUG
    @abstractmethod
    def register_logging_event(self, job_id: str, level: int, msg: str, *, only_if_not_exists: bool = False) -> None:
        pass

    @abstractmethod
    def report_slave_info(self, slave_info: SlaveInfo2) -> None:
        pass
