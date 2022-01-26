from typing import List, Tuple, Optional

from .i_printer_service import IPrinterService
from ..enums.print_file_type import PrintFileType
from ..enums.sensor import Sensor
from ..enums.sensor_type import SensorType
from ..port.adapter.brainer_client import BrainerClient
from ..repository.printer_state_repository import PrinterStateRepository


class PrinterService(IPrinterService):

    def __init__(self, printer_state_repo: PrinterStateRepository, brainer_client: BrainerClient):
        self._printer_state_repo = printer_state_repo
        self._brainer_client = brainer_client

    def load_printer(self) -> None:
        self._printer_state_repo.load_printer()

    def dump_printer(self) -> None:
        self._printer_state_repo.dump_printer()

    def is_printer_paired(self) -> bool:
        return self._printer_state_repo.is_printer_paired()

    def get_sensors(self) -> List[Sensor]:
        return self._printer_state_repo.get_sensors()

    def get_sensor_by_name(self, name: str) -> Optional[Sensor]:
        return self._printer_state_repo.get_sensor_by_name(name)

    def add_sensor(self, name: str, phasio_id: str, sensor_type: SensorType) -> None:
        sensor = Sensor(name, phasio_id, sensor_type)
        self._printer_state_repo.commit_sensor(sensor)
        self._printer_state_repo.dump_printer()

    def get_printer_id(self) -> str:
        return self._printer_state_repo.get_printer_id()

    def set_printer_id(self, printer_id: str) -> None:
        return self._printer_state_repo.set_printer_id(printer_id)

    def get_candidate_id(self) -> str:
        return self._printer_state_repo.get_candidate_id()

    def set_candidate_id(self, candidate_id: str) -> None:
        return self._printer_state_repo.set_candidate_id(candidate_id)

    def set_secret(self, secret: str) -> None:
        return self._printer_state_repo.set_secret(secret)

    def get_secret(self) -> str:
        return self._printer_state_repo.get_secret()

    def set_pairing_code(self, pairing_code: str):
        return self._printer_state_repo.set_pairing_code(pairing_code)

    def get_pairing_code(self) -> str:
        return self._printer_state_repo.get_pairing_code()

    def register_candidate(self, printer_name: str, printer_model: str, printer_material: str,
                           file_type: PrintFileType) -> None:
        pairing_code, candidate_id, secret = self._brainer_client.register_candidate(printer_name, printer_model, printer_material, file_type)
        self.set_secret(secret)
        self.set_pairing_code(pairing_code)
        self.set_candidate_id(candidate_id)
