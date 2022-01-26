from ..pyzio_settings import PyzioSettings


class BrainerConfig:

	def __init__(self, settings: PyzioSettings):
		self._settings = settings

	def host(self) -> str:
		return self._settings.brainer_host()

	def file_storage(self) -> str:
		return self._settings.print_file_storage()
