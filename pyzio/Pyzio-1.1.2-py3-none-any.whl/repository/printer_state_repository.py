import threading
from typing import List, Dict, Optional

from dependency_injector.wiring import inject, Provide

from ..enums.sensor import Sensor
from ..pyzio_settings import PyzioSettings


class PrinterStateRepository:
    @inject
    def __init__(self, settings: PyzioSettings):
        self._lock = threading.Lock()
        self._settings = settings
        self._pairing_code = None
        self._candidate_id = None
        self._printer_id = None
        self._secret = None
        self._sensors: Dict[str, Sensor] = dict()

    def set_candidate_id(self, candidate_id: str) -> None:
        self._candidate_id = candidate_id

    def get_candidate_id(self) -> str:
        return self._candidate_id

    def set_printer_id(self, printer_id: str) -> None:
        self._printer_id = printer_id

    def get_printer_id(self) -> str:
        return self._printer_id

    def get_sensors(self) -> List[Sensor]:
        return list(self._sensors.values())

    def get_sensor_by_name(self, name: str) -> Optional[Sensor]:
        return self._sensors.get(name)

    def commit_sensor(self, sensor: Sensor) -> None:
        self._sensors[sensor.name] = sensor

    def load_printer(self) -> None:
        self._printer_id = self._settings.printer_id()
        [self.commit_sensor(s) for s in self._settings.get_sensors()]
        self._secret = self._settings.printer_secret()

    def dump_printer(self) -> None:
        with self._lock:
            self._settings.set_printer_id(self._printer_id)
            self._settings.set_sensors(self.get_sensors())
            self._settings.set_printer_secret(self._secret)
            self._settings.save()

    def is_printer_paired(self) -> bool:
        if self._settings.printer_id() is not None:
            return True
        else:
            return False

    def set_secret(self, secret: str) -> None:
        self._secret = secret

    def get_secret(self) -> str:
        return self._secret

    def set_pairing_code(self, pairing_code):
        self._pairing_code = pairing_code

    def get_pairing_code(self) -> str:
        return self._pairing_code
