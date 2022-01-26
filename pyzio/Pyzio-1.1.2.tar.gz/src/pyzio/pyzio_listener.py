from abc import ABC, abstractmethod


class PyzioListener(ABC):
	@abstractmethod
	def on_pairing_code_generated(self, pairing_code: str) -> None:
		pass

	@abstractmethod
	def on_candidate_registered(self, candidate_id: str) -> None:
		pass

	@abstractmethod
	def on_printer_registered(self, printer_id: str) -> None:
		pass

	@abstractmethod
	def on_sensor_registered(self, sensor_id: str, request_id: str) -> None:
		pass

	@abstractmethod
	def on_job_received(self) -> None:
		pass

	@abstractmethod
	def on_markready_received(self) -> None:
		pass
	
	@abstractmethod
	def on_update_command_received(self) -> None:
		pass
