import traceback


class MXException(Exception):
    def __init__(self, message="Something went wrong, Please contact support"):
        self.message = message
        Exception.__init__(self, message)


class MXInvalidDataException(MXException):
    def __init__(self, message='Invalid Data'):
        self.message = message
        MXException.__init__(self, message)


class MXTooManyParametersError(MXException):
    def __init__(self, message='main function can have either 0 or 1 parameter'):
        self.message = message
        MXException.__init__(self, message)


class MXUnauthorizedDBAccess(MXException):
    def __init__(self, message='Access Denied'):
        self.message = message
        MXException.__init__(self, message)


class MXTooManyRequestsError(MXException):
    def __init__(self, message='Access Denied. Only 3 Emails are allowed per BatchJob'):
        self.message = message
        MXException.__init__(self, message)


def get_error_log(exception_info):
    try:
        exception_type, value, tb = exception_info
        return {
            "Type": exception_type.__name__,
            "Message": value.__str__(),
            "Traceback": traceback.format_tb(tb)
        }
    except Exception as ex:
        print(traceback.format_exc())
        raise ex
