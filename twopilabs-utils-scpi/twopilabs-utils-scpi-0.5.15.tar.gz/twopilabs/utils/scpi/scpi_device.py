import logging
from typing import *
from .scpi_resource import ScpiResource
from .scpi_type_base import ScpiTypes
from .scpi_transport_base import ScpiTransports
from .scpi_types import ScpiEvent
from .scpi_exceptions import ScpiErrorException

logger = logging.getLogger(__name__)

class ScpiDevice(object):
    resource: Optional[ScpiResource] = None
    transport: Optional[ScpiTransports] = None

    def __init__(self, resource: ScpiResource, **kwargs) -> None:
        self.resource = resource
        self.transport = resource.transport(resource.address, **kwargs)
        logger.info(f'open [{resource.transport._transport_class}]: {resource.address}')

    def is_open(self):
        return True if self.transport is not None else False

    def close(self) -> None:
        if self.transport is not None:
            logger.info(f'close [{self.resource.transport._transport_class}]: {self.resource.address}')
            self.transport.close()
            self.transport = None

    def reset(self) -> None:
        self.transport.reset()

    def execute(self, header: str, param: Optional[ScpiTypes] = None,
                result: Optional[Type[ScpiTypes]] = type(None)) -> ScpiTypes:
        command = header
        response = None

        if param is not None:
            command = ' '.join([header, param.compose()])

        try:
            self.transport.writeline(command)

            if result is not type(None):
                response = result.parse(self.transport)

            logger.info(
                f'exec [{type(param).__name__} -> {result.__name__}]: ' +
                f'{str(header.encode())[1:]} ({str(param)}) -> ({str(response)})')
        except Exception as e:
            logger.error(
                f'exec [{type(param).__name__} -> {result.__name__}]: ' +
                f'{str(header.encode())[1:]} ({str(param)}) -> ({str(response)}) [{repr(e)}]')

        return response

    def check_error(self) -> Optional[ScpiEvent]:
        """Checks if an error is available in the device's SCPI error queue and returns it. Returns None otherwise"""
        scpi_error = self.execute('SYST:ERR:NEXT?', result=ScpiEvent)
        if scpi_error.code != 0:
            return scpi_error
        return None

    def raise_error(self) -> None:
        """Raise a ScpiErrorException when an scpi error is in the device's SCPI error queue"""
        scpi_error = self.check_error()
        if scpi_error is not None:
            raise ScpiErrorException(scpi_error)

    def __del__(self):
        self.close()

    def __enter__(self) -> 'ScpiDevice':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()