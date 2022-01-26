from typing import Dict

from ....handlers.mqtt import *
from ....pyzio_listener import PyzioListener
from ....pyzio_logger import PyzioLogger
from ....service.job_service import JobService
from ....service.printer_service import PrinterService


class MessageHandlerFactory:
    def __init__(self, logger: PyzioLogger, job_service: JobService, update_service: UpdateService,
                 printer_service: PrinterService):
        self._logger = logger
        self._job_service = job_service
        self._update_service = update_service
        self._printer_service = printer_service

    def build(self, listener: PyzioListener) -> Dict[MessageType, MessageHandler]:
        handlers = dict()
        for handler_class in MessageHandler.__subclasses__():
            handler = handler_class(self._logger, self._job_service, self._update_service, self._printer_service,
                                    listener)
            handlers[handler.can_handle()] = handler
        return handlers
