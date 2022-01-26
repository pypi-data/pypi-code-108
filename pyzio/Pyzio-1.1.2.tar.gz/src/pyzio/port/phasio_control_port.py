from abc import ABC, abstractmethod

from ..domain.job import Job
from ..enums.print_file_type import PrintFileType


class PhasioControlPort(ABC):

	@abstractmethod
	def get_file(self, printer_id: str, secret: str, job: Job) -> str:
		pass

	@abstractmethod
	def register_candidate(self, job_id: str, filename: str, cluster_id: str, file_type: PrintFileType) -> (int, str, str):
		pass
