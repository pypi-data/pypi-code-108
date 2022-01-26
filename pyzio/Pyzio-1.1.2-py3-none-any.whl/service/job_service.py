from typing import List, Optional

from .i_job_service import IJobService
from ..pyzio_logger import PyzioLogger

from ..port.adapter.brainer_client import BrainerClient
from ..pyzio_printer import PyzioPrinter
from ..pyzio_settings import PyzioSettings
from ..repository.local_job_repository import LocalJobRepository, Job
from ..repository.printer_state_repository import PrinterStateRepository


class JobService(IJobService):

    def __init__(self, printer: PyzioPrinter, brainer_client: BrainerClient, local_job_repo: LocalJobRepository,
                 printer_state_repo: PrinterStateRepository, logger: PyzioLogger, settings: PyzioSettings):
        self._printer = printer
        self._brainer_client = brainer_client
        self._local_job_repo = local_job_repo
        self._printer_state_repo = printer_state_repo
        self._logger = logger
        self._settings = settings

    def queue_jobs(self, jobs: List[Job]) -> None:
        self._local_job_repo.update_jobs(jobs, self._settings.current_job_id())

    def peek_next_job(self) -> Optional[Job]:
        if not self._local_job_repo.is_queue_empty():
            self._logger.info('Printer has jobs in the queue.')
            return self._local_job_repo.peek_job_from_queue()
        self._logger.info('Printer has no jobs in the queue.')
        return None

    def peek_current_job(self) -> Optional[Job]:
        current_job = self._settings.current_job_id()
        if current_job is None:
            return None
        return self.get_job_by_id(current_job)

    def get_job_by_id(self, id: str) -> Optional[Job]:
        return self._local_job_repo.peek_job_by_id(id)

    def remove_job_by_id(self, id: str) -> None:
        self._local_job_repo.remove_job_by_id(id)

    def download_next_job(self) -> None:
        if not self._local_job_repo.is_queue_empty():
            self._logger.info('Printer has jobs in the queue.')
            job = self._local_job_repo.peek_job_from_queue()
            self._get_next_job_file(job)
        self._logger.info('Printer has no jobs in the queue.')
        return None

    def start_next_job(self) -> Optional[Job]:
        if not self._local_job_repo.is_queue_empty():
            self._logger.info('There are one or more jobs in the queue')
            job = self._local_job_repo.peek_job_from_queue()
            job = self._get_next_job_file(job)
            self._printer.start_printing(job)
            return job
        self._logger.info('Printer has no job to start.')
        return None

    def _get_next_job_file(self, job: Job) -> Job:
        self._logger.info('Fetched top job')
        printer_id, secret = self._printer_state_repo.get_printer_id(), self._printer_state_repo.get_secret()
        self._logger.info('Got secret and printer ID from the state repo')
        self._brainer_client.get_file(printer_id, secret, job)
        self._logger.info('Collected file from Brainer')
        return job
