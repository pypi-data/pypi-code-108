from .i_platform_emitter import IPlatformEmitter
from ..pyzio_listener import PyzioListener
from ..pyzio_logger import PyzioLogger
from ..service.i_printer_service import IPrinterService


class PlatformListener(PyzioListener):

    def __init__(self, logger: PyzioLogger, listener: PyzioListener,
                 printer_service: IPrinterService, emitter: IPlatformEmitter):
        self._logger = logger
        self._listener = listener
        self._printer_service = printer_service
        self._emitter = emitter

    def on_candidate_registered(self, candidate_id: str):
        self._printer_service.set_candidate_id(candidate_id)
        self._listener.on_candidate_registered(candidate_id)

    def on_pairing_code_generated(self, pairing_code: str) -> None:
        self._printer_service.set_pairing_code(pairing_code)
        self._listener.on_pairing_code_generated(pairing_code)

    def on_printer_registered(self, printer_id: str):
        self._printer_service.set_candidate_id('')
        self._printer_service.set_pairing_code('')
        self._printer_service.dump_printer()
        self._emitter.disconnect()
        self._emitter.connect_as_printer()
        self._listener.on_printer_registered(printer_id)

    def on_sensor_registered(self, sensor_id: str, request_id: str):
        self._listener.on_sensor_registered(sensor_id, request_id)

    def on_job_received(self) -> None:
        self._listener.on_job_received()

    def on_markready_received(self) -> None:
        self._listener.on_markready_received()

    def on_update_command_received(self) -> None:
        self._logger.info('update command received')
