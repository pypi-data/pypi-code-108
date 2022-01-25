class ErrorType:
    # only these two get reported to CIP
    ERROR_CONFIG  = "THIRD-PARTY-CONFIG"
    ERROR_GENERIC = "THIRD-PARTY-GENERIC"

    # error returned by CNC framework
    ERROR_FRAMEWORK  = "FIRST-PARTY-GENERIC"


class SDKException(Exception):
    def __init__(self, *args, **kwargs):
        self.error_code = kwargs.pop("error_code", 500)
        super(SDKException, self).__init__(*args, **kwargs)

class StoreException(SDKException):
    pass


class SendDataException(SDKException):
    pass


class FetchException(SDKException):
    pass


class InValidConfigException(SDKException):
    pass


class FetchConfigException(SDKException):
    pass


class AuthException(SDKException):
    pass