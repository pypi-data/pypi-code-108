from abc import ABC, abstractmethod

from ..enums.job_status import JobStatus
from ..enums.sensor_type import SensorType
from ..pyzio_listener import PyzioListener


class PhasioMQTTPort(ABC):

    @abstractmethod
    def connect_as_candidate(self, candidate_id: str, secret: str, listener: PyzioListener) -> None:
        pass

    @abstractmethod
    def connect_as_printer(self, printer_id: str, secret: str, listener: PyzioListener) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def register_sensor(self, sensor_name: str, sensor_type: SensorType) -> str:
        pass

    @abstractmethod
    def stream_sensor_data(self, sensor_id: str, sensor_type: SensorType, value: float) -> None:
        pass

    @abstractmethod
    def send_job_updates(self, job_id: str, status: JobStatus) -> None:
        pass

    @abstractmethod
    def send_heartbeat(self) -> None:
        pass