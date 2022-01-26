from abc import ABCMeta, abstractmethod

from .pyzio_listener import PyzioListener
from .service.i_job_service import IJobService


class IPyzio(metaclass=ABCMeta):

    @abstractmethod
    def initialise_printer(self):
        pass

    @abstractmethod
    def set_listener(self, listener: PyzioListener):
        pass

    @abstractmethod
    def get_printer_service(self):
        pass

    @abstractmethod
    def get_job_service(self) -> IJobService:
        pass

    @abstractmethod
    def get_platform_emitter(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass