from abc import abstractmethod, ABC
from typing import Optional

from ..domain.job import Job


class IJobService(ABC):
    @abstractmethod
    def queue_jobs(self, jobs):
        pass

    @abstractmethod
    def peek_next_job(self):
        pass

    @abstractmethod
    def get_job_by_id(self, id: str):
        pass

    @abstractmethod
    def remove_job_by_id(self, id: str):
        pass

    @abstractmethod
    def peek_current_job(self) -> Optional[Job]:
        pass

    @abstractmethod
    def _get_next_job_file(self, job):
        pass

    @abstractmethod
    def download_next_job(self):
        pass

    @abstractmethod
    def start_next_job(self) -> Optional[Job]:
        pass