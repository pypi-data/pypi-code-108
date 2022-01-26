from typing import Optional

from polysynth.types import Response

class PolysynthException(Exception):
    """
    Custom exception for Polysynth SDK
    """

    def __init__(self, status_code, err_code, err_msg, data=None) -> None:
        super().__init__(status_code, err_code, err_msg, data)
        self._status_code = status_code
        self._err_code = err_code
        self._err_msg = err_msg
        self._data = data
    

    def __str__(self):
        return Response(self._status_code, self._err_code, self._err_msg, self._data).__str__()

class MissingInputError(PolysynthException): pass

class InvalidFormatError(PolysynthException): pass

class ConnectionError(PolysynthException): pass

class InvalidSchemaError(PolysynthException): pass

class RPCTimeoutError(PolysynthException): pass

class InvalidParameterError(PolysynthException): pass

class InsufficientWalletBalanceError(PolysynthException): pass

class InsufficientMaticError(PolysynthException): pass

class LowGasError(PolysynthException): pass

class TransactionFailedError(PolysynthException): pass





