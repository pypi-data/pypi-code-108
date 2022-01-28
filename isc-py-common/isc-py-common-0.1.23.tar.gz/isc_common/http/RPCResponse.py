from enum import IntEnum

from django.db.models import QuerySet


class Class:
    def __init__(self):
        self._excluded_keys = ["_excluded_keys"]

    def querySetToDict(self, vqs):
        return [item for item in vqs]

    @property
    def dict(self):
        return dict((key, value) for (key, value) in self.__dict__.items() if value is not None and key not in self._excluded_keys)


class RPCResponseConstant(IntEnum):
    statusSuccess = 0
    statusOffline = 1
    statusFailure = -1
    statusValidationError = -4
    statusLoginIncorrect = -5
    statusMaxLogginAttemptsExceeded = -6
    statusLoginRequired = -7
    statusLoginSuccess = -8
    statusUpdateWithoutPkError = -9
    statusTransactionFailed = -10
    statusTransportError = -90
    statusUnknownHostError = -91
    statusConnetionResetError = -92
    statusServerTimeout = -100
    statusNoFileAttached = -101


class RPCResponse(Class):

    def __init__(self, clientContext=None, data=None, httpHeaders=None, httpResponseCode=None, httpResponseText=None, status=0, transactionNum=None):
        Class.__init__(self)
        self.clientContext = clientContext
        if isinstance(data, QuerySet):
            self.data = self.querySetToDict(data)
        elif isinstance(data, list):
            self.data = data
        elif isinstance(data, dict):
            self.data = data
        self.httpHeaders = httpHeaders
        self.httpResponseCode = httpResponseCode
        self.httpResponseText = httpResponseText
        self.status = status
        self.transactionNum = transactionNum
