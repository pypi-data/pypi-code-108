from typing import List, Tuple

from src.pyzio.pyzio_settings import PyzioSettings


class StateConfig:

    def __init__(self, settings: PyzioSettings):
        self._settings = settings

    def printer_id(self) -> str:
        return self._settings.printer_id()

    def candidate_id(self) -> str:
        return self._settings.candidate_id()

    def pairing_id(self) -> str:
        return self._settings.pairing_id()

    def sensor_ids(self) -> List[Tuple[str, str]]:
        return self.sensor_ids()
