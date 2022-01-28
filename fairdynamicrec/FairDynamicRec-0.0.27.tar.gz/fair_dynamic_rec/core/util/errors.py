import logging

class FairDynamicRecException(Exception):
    """Exceptions raised during the compilation of FairDynamicRec

    Attributes:
        element_name -- element which caused the error
        message -- explanation of the error
    """

    def __init__(self, elem_name, message="LibRec-Auto Exception."):
        self.element_name = elem_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.element_name} -> {self.message}'


class InvalidConfiguration(FairDynamicRecException):
    """Exception raised for errors in the configuration file XML.
    """

    # may want to make it less broad, go into more detail
    def __init__(self, elem_name, message="Error processing configuration file."):
        super().__init__(elem_name, message)
        self._write_to_log()

    def _write_to_log(self):
        logging.error(f' Configuration file: {self.element_name}: {self.message}')