from .scpi_types import ScpiEvent


class ScpiException(Exception):
    """This class represents a generic SCPI Error"""
    pass


class ScpiErrorException(ScpiException):
    """This class represents a SCPI Error found in the SYST:ERR queue of the device"""
    def __init__(self, scpi_error: ScpiEvent):
        self.scpi_error = scpi_error
        super().__init__(scpi_error)


class ScpiTransportException(IOError):
    pass
