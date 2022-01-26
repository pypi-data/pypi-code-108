import uuid
from datetime import datetime

import pytz

from ....enums.job_status import JobStatus
from ....enums.sensor_type import SensorType


class MessageFactory:

    def create_sensor_registration_message(self, sensor_name: str, printer_id: str, sensor_type: SensorType):
        r_id = self._generate_uuid()
        reading = {
            'requestId': r_id,
            'printerId': printer_id,
            'sensorName': sensor_name,
            'sensorType': sensor_type,
            'measurementTime': self._get_date()
        }
        return reading, r_id

    def create_reading_message(self, sensor_id: str, sensor_type: SensorType, value: float):
        reading = {
            'requestId': self._generate_uuid(),
            'sensorId': sensor_id,
            'type': sensor_type.name,
            'value': value,
            'measurementTime': self._get_date()
        }
        return reading

    def create_job_update_message(self, job_id: str, printer_id: str, status: JobStatus):
        job_update = {
            'jobId': job_id,
            'requestId': self._generate_uuid(),
            'printerId': printer_id,
            'status': status,
            'measurementTime': self._get_date()
        }
        return job_update

    def create_heartbeat_message(self, printer_id: str):
        heartbeat = {
            'printerId': printer_id,
            'requestId': self._generate_uuid(),
            'printerStatus': "CONNECTED",
            'measurementTime': self._get_date()
        }
        return heartbeat

    def _get_date(self) -> str:
        return pytz.utc.localize(datetime.utcnow()).isoformat()

    def _generate_uuid(self) -> str:
        return str(uuid.uuid4())
