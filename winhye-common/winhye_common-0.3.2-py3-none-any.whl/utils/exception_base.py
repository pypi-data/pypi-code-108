import enum

__all__ = ["ExceptionCode", "WinhyeException", "OSSException", "ConfigException"]


# exception codes
class ExceptionCode(enum.Enum):
    DB = 1
    OSS = 2
    mqtt = 3
    config = 4


class WinhyeException(Exception):
    def __init__(self, code: ExceptionCode, message: str):
        self.code = code.value
        self.message = message

    def __str__(self):
        return "{exception}: winhye-common error code={code}, message={message}".format(
            exception=self.__class__.__name__,
            code=self.code,
            message=self.message
        )


class OSSException(WinhyeException):
    """OSS exception
    """

    def __init__(self, message: str):
        super(OSSException, self).__init__(ExceptionCode.OSS, message)


class ConfigException(WinhyeException):
    """config exception
    """

    def __init__(self, message: str):
        super(ConfigException, self).__init__(ExceptionCode.config, message)
