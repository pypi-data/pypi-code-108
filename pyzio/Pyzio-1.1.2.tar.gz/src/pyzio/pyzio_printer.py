from abc import ABC, abstractmethod

from .domain.job import Job
from .enums.print_file_type import PrintFileType


class PyzioPrinter(ABC):
	@abstractmethod
	def start_printing(self, job: Job) -> bool:
		pass

	@abstractmethod
	def delete_file_from_storage(self, path: str) -> None:
		pass

	@abstractmethod
	def printer_name(self) -> str:
		pass

	@abstractmethod
	def printer_model(self) -> str:
		pass

	@abstractmethod
	def printer_material(self) -> str:
		pass

	@abstractmethod
	def printer_filetype(self) -> PrintFileType:
		pass
