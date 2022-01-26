import threading
from typing import Optional
import time

from dependency_injector.wiring import Provide, inject

from .i_platform_emitter import IPlatformEmitter
from .platform_listener import PlatformListener
from ..domain.job import Job
from ..enums.job_status import JobStatus
from ..enums.sensor_type import SensorType
from ..port.phasio_mqtt_port import PhasioMQTTPort
from ..pyzio_listener import PyzioListener
from ..pyzio_logger import PyzioLogger
from ..pyzio_printer import PyzioPrinter
from ..pyzio_settings import PyzioSettings
from ..service.i_job_service import IJobService
from ..service.i_printer_service import IPrinterService


class PlatformEmitter(IPlatformEmitter):

    @inject
    def __init__(self, logger: PyzioLogger, printer: PyzioPrinter, phasio_port: PhasioMQTTPort,
                 printer_service: IPrinterService, job_service: IJobService, settings: PyzioSettings):
        self._logger = logger
        self._printer = printer
        self._settings = settings
        self._phasio_port = phasio_port
        self._printer_service = printer_service
        self._job_service = job_service
        self._listener: Optional[PlatformListener] = None

    def set_listener(self, listener: PyzioListener) -> None:
        self._listener = PlatformListener(self._logger, listener, self._printer_service, self)

    def connect_as_printer(self) -> None:
        printer_id = self._printer_service.get_printer_id()
        secret = self._printer_service.get_secret()
        self._phasio_port.connect_as_printer(printer_id, secret, self._listener)
        heartbeat_thread = threading.Thread(target=self._heartbeat, daemon=True)
        heartbeat_thread.start()

    def disconnect(self) -> None:
        self._phasio_port.disconnect()

    def is_mqtt_connected(self) -> bool:
        return self._phasio_port.is_connected()

    def send_sensor_registration(self, sensor_name: str, sensor_type: SensorType) -> str:
        return self._phasio_port.register_sensor(sensor_name, sensor_type)

    def mark_job_failed(self, job_id: str):
        self._settings.set_current_job_id(None)
        self._job_service.remove_job_by_id(job_id)
        self._phasio_port.send_job_updates(job_id, status=JobStatus.FAILED)

    def mark_job_complete(self, job_id: str, filepath: str):
        self._printer.delete_file_from_storage(filepath)
        self._settings.set_current_job_id(None)
        self._job_service.remove_job_by_id(job_id)
        self._phasio_port.send_job_updates(job_id, status=JobStatus.COMPLETED)

    def mark_job_in_progress(self, job_id: str):
        self._settings.set_current_job_id(job_id)
        self._phasio_port.send_job_updates(job_id, status=JobStatus.IN_PROGRESS)

    def send_sensor_update(self, sensor_id: str, value: float, sensor_type: SensorType = SensorType.TEMPERATURE):
        self._phasio_port.stream_sensor_data(sensor_id, sensor_type, value)

    def register_candidate(self):
        self._printer_service.register_candidate(self._printer.printer_name(),
                                                 self._printer.printer_model(),
                                                 self._printer.printer_material(),
                                                 self._printer.printer_filetype())
        candidate_id = self._printer_service.get_candidate_id()
        secret = self._printer_service.get_secret()
        self._phasio_port.connect_as_candidate(candidate_id, secret, self._listener)

    def start_next_job(self) -> Optional[Job]:
        return self._job_service.start_next_job()

    def _heartbeat(self):
        while True:
            self._phasio_port.send_heartbeat()
            time.sleep(30)
