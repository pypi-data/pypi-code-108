
class ExceptionsConfig:
    SUPPRESS_EXCEPTIONS = False


class CnvrgError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class CnvrgArgumentsError(CnvrgError):
    def __init__(self, error):
        """
        This error aggregate multiple bad argument errors into one.
        Use when the user gave multiple wrong arguments and should be notified about all of them at once.
        @param error_dict: dict. Key is the argument's name and the value is the message regarding the argument.
        @return:  None
        """
        message = "Bad arguments: "
        if isinstance(error, dict):
            message += "\r\n "
            for key in error.keys():
                if len(error.keys()) > 1:
                    message += ", \r\n"
                message += str(key) + ": " + str(error[key])
        else:
            message += error

        super(CnvrgError, self).__init__(message)


class CnvrgFinalStateReached(CnvrgError):
    def __init__(self, message):
        super(CnvrgError, self).__init__(message)


class CnvrgHttpError(CnvrgError):
    def __init__(self, status_code, message):
        self.status_code = status_code
        super(CnvrgError, self).__init__(message)


class CnvrgFileError(CnvrgError):
    def __init__(self, message):
        super(CnvrgError, self).__init__(message)


class CnvrgRetryError(CnvrgError):
    def __init__(self, message):
        super(CnvrgError, self).__init__(message)


class CnvrgLoginError(CnvrgError):
    def __init__(self, message):
        super(CnvrgError, self).__init__(message)
