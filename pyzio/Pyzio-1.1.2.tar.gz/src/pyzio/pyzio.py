from dependency_injector import providers

from .i_pyzio import IPyzio
from .inject.container import PyzioContainer
from .pyzio_listener import PyzioListener
from .pyzio_logger import PyzioLogger
from .pyzio_printer import PyzioPrinter
from .pyzio_settings import PyzioSettings
from .resource.platform_emitter import PlatformEmitter
from .service.i_job_service import IJobService
from .service.i_printer_service import IPrinterService


class Pyzio(IPyzio):

    def __init__(self, logger: PyzioLogger, printer: PyzioPrinter, settings: PyzioSettings):
        self._logger = logger
        self._settings = settings
        logger = providers.Object(logger)
        printer = providers.Object(printer)
        settings = providers.Object(settings)
        pyzio_container = PyzioContainer(logger=logger, printer=printer, settings=settings)
        self._emitter = pyzio_container.emitter()
        self._printer_service = pyzio_container.printer_service()
        self._job_service = pyzio_container.job_service()

    def initialise_printer(self):
        if not self._printer_service.is_printer_paired():
            self._emitter.register_candidate()
        else:
            self._printer_service.load_printer()
            self._emitter.connect_as_printer()

    def set_listener(self, listener: PyzioListener):
        self._emitter.set_listener(listener)

    def get_printer_service(self) -> IPrinterService:
        return self._printer_service

    def get_job_service(self) -> IJobService:
        return self._job_service

    def get_platform_emitter(self) -> PlatformEmitter:
        return self._emitter

    def shutdown(self):
        self._emitter.disconnect()
        self._logger.info('Disconnected from the Broker')
        self._settings.save()
