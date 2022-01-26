from abc import ABC, abstractmethod

from ..enums.message_type import MessageType
from ..pyzio_listener import PyzioListener
from ..pyzio_logger import PyzioLogger
from ..repository.local_job_repository import Job
from ..service.job_service import JobService
from ..service.printer_service import PrinterService
from ..service.update_service import UpdateService


class MessageHandler(ABC):
    def __init__(self, logger: PyzioLogger, job_service: JobService, update_service: UpdateService,
                 printer_service: PrinterService, listener: PyzioListener):
        self._job_service = job_service
        self._update_service = update_service
        self._logger = logger
        self._printer_service = printer_service
        self._listener = listener

    @abstractmethod
    def handle(self, payload: dict) -> None:
        pass

    @abstractmethod
    def can_handle(self) -> MessageType:
        pass


class JobUpdateMessageHandler(MessageHandler):
    def handle(self, payload: dict) -> None:
        jobs = payload['jobs']
        self._logger.info("Received " + str(len(jobs)) + " jobs from server")
        result = []
        for job in jobs:
            seq_number, job_id, cluster_id = job['sequenceNumber'], str(job['jobId']), str(job['clusterId'])
            team_id, part_id, print_file = str(job['teamId']), str(job['partId']), str(job['printFile'])
            filename = job['filename']
            new_job = Job(seq_number, part_id, job_id, filename, cluster_id, team_id, print_file)
            result.append(new_job)
        self._job_service.queue_jobs(result)
        self._listener.on_job_received()

    def can_handle(self) -> MessageType:
        return MessageType.JOB_UPDATE_MESSAGE


class PrinterRegistrationMessageHandler(MessageHandler):
    def handle(self, payload: dict) -> None:
        self._logger.info("Printer registered by server with ID " + str(payload['printerId']))
        printer_id = str(payload['printerId'])
        candidate_id = str(payload['pairingCandidateId'])
        if self._printer_is_not_paired() and candidate_id == self._printer_service.get_candidate_id():
            self._printer_service.set_printer_id(printer_id)
            self._listener.on_printer_registered(printer_id)

    def can_handle(self) -> MessageType:
        return MessageType.PRINTER_REGISTRATION_MESSAGE

    def _printer_is_not_paired(self):
        return self._printer_service.get_printer_id() is None


class SensorRegistrationMessageHandler(MessageHandler):
    def handle(self, payload: dict) -> None:
        self._logger.info('Received sensor ack')
        sensor_id = payload['sensorId']
        request_id = payload['requestId']
        self._listener.on_sensor_registered(sensor_id, request_id)

    def can_handle(self) -> MessageType:
        return MessageType.SENSOR_REGISTRATION_MESSAGE


class PrinterActivityStatusUpdateHandler(MessageHandler):
    def handle(self, payload: dict) -> None:
        self._logger.info("Received activity status update to " + str(payload['activityState']) + " from server")
        self._listener.on_markready_received()

    def can_handle(self) -> MessageType:
        return MessageType.ACTIVITY_STATUS_UPDATE_MESSAGE


class UpdateCommandHandler(MessageHandler):
    def handle(self, payload: dict) -> None:
        version = str(payload['version'])
        self._logger.info("Received update command to version  " + version + " from server")
        self._update_service.do_update(version)
        self._listener.on_update_command_received()

    def can_handle(self) -> MessageType:
        return MessageType.UPDATE_COMMAND_MESSAGE
